from django import forms
from datetime import datetime

from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import *

import base64


class AddSMSForm(forms.ModelForm):
    """ Класс для обработки формы отправки данных СМС """

#    def __init__(self, *args, **kwargs):    # Конструктор формы
#        super().__init__(*args, **kwargs)

    class Meta:
        model = SMSData          # Связь модели с формой
        fields = ['content', ]    # Какие поля необходимо отобразить в форме.
        widgets = {                                                    # Добавление аттрибутов для тегов
            'content': forms.TextInput(attrs={'class': 'sms-input', "width": 1000}),
        }

    def process_sms_data(self):
        """ Обработка данных из СМС """
        print(self.cleaned_data['content'])
        decode_bytes = base64.b64decode(self.cleaned_data['content'])  # Получаем массив байт из base64
        print(''.join('{:02x}'.format(x) for x in decode_bytes))
        last_sms = SMSData.objects.first()  #  После изменения сортировки по убыванию времени,
                                            #  необходимо применить first - это и будет последняя СМС
        # last_sms = SMSData.objects.last()
        # sms_meta_data = ParsedMetaData.objects.create(sms=sms)
        sms_meta_data = ParsedMetaData()
        sms_meta_data.sms = last_sms
        data_from_buf = self.restore_data_from_buf_in_bits(decode_bytes, 32, 0)  # Время отправления СМС
        print(datetime.utcfromtimestamp(data_from_buf).strftime('%Y-%m-%d %H:%M:%S'))
        # sms_meta_data.sms_generation_time = data_from_buf
        sms_meta_data.sms_generation_time = datetime.utcfromtimestamp(data_from_buf).strftime('%Y-%m-%d %H:%M:%S')

        data_from_buf = self.restore_data_from_buf_in_bits(decode_bytes, 12, 32)  # Напряжение под нагрузкой
        data_from_buf += 4096
        sms_meta_data.vbat_hi = data_from_buf
        print(data_from_buf)

        data_from_buf = self.restore_data_from_buf_in_bits(decode_bytes, 12, 44)  # Время работы модема
        sms_meta_data.modem_work_time = data_from_buf
        print(data_from_buf)

        data_from_buf = self.restore_data_from_buf_in_bits(decode_bytes, 11, 56)  # Счетчик включений дальномера / 10
        data_from_buf *= 10
        sms_meta_data.range_counter = data_from_buf
        print(data_from_buf)

        data_from_buf = self.restore_data_from_buf_in_bits(decode_bytes, 10, 67)  # Счетчик попыток отправки СМС / 10
        data_from_buf *= 10
        sms_meta_data.sms_attempt_counter = data_from_buf
        print(data_from_buf)

        data_from_buf = self.restore_data_from_buf_in_bits(decode_bytes, 11, 77)  # Счетчик подтвержденных СМС
        sms_meta_data.sms_confirmed_counter = data_from_buf
        print(data_from_buf)

        data_from_buf = self.restore_data_from_buf_in_bits(decode_bytes, 22, 88)  # Долгота * 10000 СМС
        if (data_from_buf & 0x200000) == 0x200000:  # Отрицательное значение
            data_from_buf &= ~0x200000
            data_from_buf = 0 - data_from_buf
        print(float(data_from_buf/10000))
        sms_meta_data.longitude = float(data_from_buf/10000)

        data_from_buf = self.restore_data_from_buf_in_bits(decode_bytes, 21, 110)  # Широта * 10000 СМС
        if (data_from_buf & 0x100000) == 0x100000:  # Отрицательное значение
            data_from_buf &= ~0x100000
            data_from_buf = 0 - data_from_buf
        print(float(data_from_buf/10000))
        sms_meta_data.latitude = float(data_from_buf / 10000)

        data_from_buf = self.restore_data_from_buf_in_bits(decode_bytes, 12, 131)  # Напряжение без нагрузки
        data_from_buf += 4096
        print(data_from_buf)
        sms_meta_data.vbat_low = data_from_buf

        data_from_buf = self.restore_data_from_buf_in_bits(decode_bytes, 3, 143)  # Reserved. From Accel, Work from LSI
        if (data_from_buf & 0x001) == 0x001:  # СМС от акселерометра
            print('from_accel = 1')
        if (data_from_buf & 0x002) == 0x002:  # Работа от LSI
            print('work_from_LSI = 1')
        sms_meta_data.from_accel = data_from_buf & 0x001
        sms_meta_data.work_from_LSI = data_from_buf & 0x002
        sms_meta_data.save()
        return sms_meta_data.pk

    @staticmethod
    def restore_data_from_buf_in_bits(sms_binary_buf, var_length, var_offset):
        """ Восстановление значения из буфера """
        byte_index = int(var_offset // 8)  # Индекс нужного перевого байта в буфере (целая часть от деления)
        bit_offset = int(var_offset % 8)  # Смещение битов от начала байта
        cycles = int(((var_length + bit_offset) / 8) + 1)  # Кол-во циклов для получения полного значения

        # Собираем переменную из массива
        temp_data = 0
        for i in range(cycles):
            temp_data_addition = sms_binary_buf[byte_index + i]
            temp_data_addition <<= 8*i
            temp_data = temp_data | temp_data_addition

        temp_data >>= bit_offset
        var = temp_data & 0xFFFFFFFF

        # Занулили лишние биты
        # Маска для зануления лишних бит
        zero_mask = 2 ** var_length - 1
        var &= zero_mask

        return var


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-input'}))
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput(attrs={'class': 'form-input'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
