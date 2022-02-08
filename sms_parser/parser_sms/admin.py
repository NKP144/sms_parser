from django.contrib import admin
from .models import *

# Register your models here.


class SMS_dataAdmin(admin.ModelAdmin):
    """Класс-редактор для задания параметров представления модели"""
    list_display = ('content', 'time_created')  # Поля, которые выводятся в списке записей


admin.site.register(SMS_data, SMS_dataAdmin)
