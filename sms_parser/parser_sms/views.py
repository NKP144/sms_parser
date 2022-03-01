import io, base64

import numpy as np
from django.contrib.auth import logout, login
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView
from .forms import *

import matplotlib
# matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates
from datetime import datetime

# Create your views here.

menu = [{'title': "О сайте", 'url_name': 'about'},
        {'title': "Обработать СМС", 'url_name': 'process_sms'},
        {'title': "Обратная связь", 'url_name': 'contact'},
        ]


class AddSMS(CreateView):
    """ Класс для отображения формы ввода СМС """
    # Связываем форму для отображения
    form_class = AddSMSForm
    # Связываем шаблон для отображения
    template_name = 'parser_sms/process_sms.html'
    # Связываем ссылку для отображения в случае успешной отправки данных формы
    #success_url = reverse_lazy('parsed_sms', args=[1])

    def get_context_data(self, *, object_list=None, **kwargs):  #
        """ Функция для передачи и статического и динамического контекста """
        # Взять уже существующий контекст
        context = super().get_context_data(**kwargs)
        context['title'] = 'Обработка СМС'

        user_menu = menu.copy()
        if not self.request.user.is_authenticated:
            user_menu.pop(1)
        context['menu'] = user_menu

        return context

    def form_valid(self, form):     # Метод вызывается до того, как данные будут записаны в БД
        form.save() # Сохранили данные в БД
        self.kwargs['pk'] = form.process_sms_data()     # Обработать полученную СМС и вернуть pk метаданных
        # Увстанавливаем pk для получения url в методе get_success_url
        # sms = SMSData.objects.first() #  После изменения сортировки по убыванию времени,
                                      #  необходимо применить first - это и будет последняя СМС
        # self.kwargs['pk'] = sms.pk
        # metadata = ParsedMetaData.objects.get(sms__id='32').pk
        # metadata = ParsedMetaData.objects.get(sms=sms)
        # self.kwargs['pk'] = metadata.pk
        return super(CreateView, self).form_valid(form)     # Данные в БД записываются после этого вызова,
                                                            # если ранее не был вызван метод form.save()

    def get_success_url(self):
        # sms = SMSData.objects.last()
        # return reverse_lazy('parsed_sms', args=[sms.pk])
        # Возвращает URL вида parsed_sms/sms_id. Т.к. в методе form_valid в качестве пар-ра pk берется pk.sms -
        # id объкта SMSData
        return reverse_lazy('parsed_sms', args=[self.kwargs['pk']])
        # Вот тут можно вернуть в качестве pk - id объекта ParsedMetaData


class ShowParsedSMS(DetailView):
    model = ParsedMetaData
    template_name = 'parser_sms/parsed_sms.html'
    # pk_url_kwarg = 'sms_id'
    pk_url_kwarg = 'metadata_id'
    context_object_name = 'parsed_sms'

    def get_context_data(self, *, object_list=None, **kwargs):  #
        """ Функция для передачи и статического и динамического контекста """
        # Взять уже существующий контекст
        context = super().get_context_data(**kwargs)
        context['title'] = 'Результаты обработки СМС'

        user_menu = menu.copy()
        if not self.request.user.is_authenticated:
            user_menu.pop(1)
        context['menu'] = user_menu
        # Добавить в контекст все данные с измерениями. Данные получаем используя обЪект parsed_sms (модель ParsedMetaData)
        context['measure_objects'] = context['parsed_sms'].sms.parsedmeasuredata_set.filter(sms_id=context['parsed_sms'].sms.id)

        # Формируем график
        context['chart'] = self.form_graph_image(context['parsed_sms'].sms.id)

        return context

    @staticmethod
    def form_graph_image(sms_id):
        measure_data_set = ParsedMeasureData.objects.filter(sms_id=sms_id)

        temparature_list = [measure_data.temperature for measure_data in measure_data_set]
        range_list = [measure_data.range for measure_data in measure_data_set]
        dateime_list = [measure_data.measure_time for measure_data in measure_data_set]

        # matplotlib.use('Agg')

        # Преобразовать данные для matplotlib
        temp_mp = np.array(temparature_list)
        range_mp = np.array(range_list)
        xdata_float = matplotlib.dates.date2num(dateime_list)

        fig = plt.figure(figsize=(10, 10))   # Создать фигуру
        fig.suptitle('Графики изменения температуры и уровня наполнения')

        ax1 = fig.add_subplot(2, 1, 1)      # Добавляем две оси
        ax2 = fig.add_subplot(2, 1, 2)

        ax1.set_xlabel('Время')
        ax2.set_xlabel('Время')

        ax1.set_ylabel('Температура, °C')
        ax2.set_ylabel('Напряжение, мВ')

        ax1.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M\n%y-%m-%d'))
        ax1.plot_date(xdata_float, temp_mp, 'r-o')

        ax2.bar(xdata_float, range_mp, width=0.025, linewidth=2, edgecolor='r')
        ax2.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M\n%y-%m-%d'))

        ax1.grid()
        ax2.grid()

        flike = io.BytesIO()
        fig.savefig(flike)
        # plt.savefig('save_fig.png')
        # plt.savefig(flike)
        # plt.show()  # Функция нужна чтобы не закрывалось окно с графиком
        return base64.b64encode(flike.getvalue()).decode()

# ----------------------------------------------------------------------------------------------------------------------
""" Пытался отобразить объект модели ParsedMetaData по sms_id. Не вышло. При подмене pk_url_kwarg на id нужного 
    элемента, Django вывел ошибку, что pk должен совпадать с pk указанным в URL. А в этом URL указывается sms_id """
    # def get_object(self, queryset=None):
    #     sms_id = self.kwargs.get(self.pk_url_kwarg, None)
    #     self.pk_url_kwarg = ParsedMetaData.objects.get(sms__id=sms_id).pk
    #     return super().get_object()

    # def get_queryset(self):
    #     sms_id = self.kwargs.get(self.pk_url_kwarg, None)
    #     q = super().get_queryset()
    #     return q.filter(sms__id=sms_id)
    #     # return ParsedMetaData.objects.get(sms__id=sms_id)

# ----------------------------------------------------------------------------------------------------------------------
# def index(request):
#     if request.method == 'POST':            # Проверка метода запроса. Если ответ из формы, то метод будет POST
#         form = AddSMSForm(request.POST)     # Заполняем форму данными из запроса и файлами
#         if form.is_valid():                 # Проверка валидности данных формы
#             form.save()                     # Сохраняем данные в базу
#             return redirect('home_page')    # Возвращает заполненную форму обратно
#     else:
#         form = AddSMSForm()
#
#     context = {
#         'title': 'Расшифровка СМС',
#         'form': form,
#     }
#
#     return render(request, 'parser_sms/index.html', context=context)
# ----------------------------------------------------------------------------------------------------------------------


def index(request):
    return render(request, 'parser_sms/index.html', {'menu': menu, 'title': 'Главная страница'})


class ListAddedSMS(ListView):
    """ Класс-представления для отображения списка обработанных СМС"""
    paginate_by = 5     # Пагинатор, для постраничного вывода списка
    model = SMSData
    template_name = 'parser_sms/index.html'
    context_object_name = 'processed_sms'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Главная страница'

        user_menu = menu.copy()
        if not self.request.user.is_authenticated:
            user_menu.pop(1)
        context['menu'] = user_menu

        return context
        # c_def = self.get_user_context(title="Главная страница")  # Формируем доп. контекс в функции из класса DataMixin
        # return dict(list(context.items()) + list(c_def.items()))

    # def get_queryset(self):  # Метод для выбора из модели только необходимых записей
    #     return SMSData.objects.filter(parsedmetadata__id__gte=0)  # Выбрать СМС, кторые были точно обработаны


def about(request):  # HttpRequest
    return render(request, 'parser_sms/about.html', {'menu': menu, 'title': 'О сайте'})


def contact(request):
    return render(request, 'parser_sms/contact.html', {'menu': menu, 'title': 'Обратная связь'})


class LoginUser(LoginView):
    """ Класс-представление для авторизации пользователя в системе """
    form_class = LoginUserForm
    template_name = 'parser_sms/login.html'

    # def get_context_data(self, *, object_list=None, **kwargs):  # Функция для передачи и статического и динамического контекста
    #     context = super().get_context_data(**kwargs)  # Взять уже существующий контекст
    #     c_def = self.get_user_context(title='Авторизация')  # Формируем доп. контекс в функции из класса DataMixin
    #     return dict(list(context.items()) + list(c_def.items()))  # Возвраст словаря с контекстом

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Авторизация'

        user_menu = menu.copy()
        if not self.request.user.is_authenticated:
            user_menu.pop(1)
        context['menu'] = user_menu

        return context

    def get_success_url(self):
        return reverse_lazy('home_page')


def logout_user(request):
    logout(request)
    return redirect('login')


class RegisterUser (CreateView):
    """ Класс-представления для регистрации пользователя """
    form_class = RegisterUserForm
    template_name = 'parser_sms/register.html'
    success_url = reverse_lazy('login')

    # def get_context_data(self, *, object_list=None, **kwargs): # Функция для передачи и статического и динамического контекста
    #     context = super().get_context_data(**kwargs)  # Взять уже существующий контекст
    #     c_def = self.get_user_context(title='Регистрация')  # Формируем доп. контекс в функции из класса DataMixin
    #     return dict(list(context.items()) + list(c_def.items()))  # Возвраст словаря с контекстом

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Регистрация'

        user_menu = menu.copy()
        if not self.request.user.is_authenticated:
            user_menu.pop(1)
        context['menu'] = user_menu

        return context

    def form_valid(self, form):
        user = form.save()  # Сохранили пользователя в БД
        login(self.request, user)  # Авторизация пользователя
        return redirect('home_page')
