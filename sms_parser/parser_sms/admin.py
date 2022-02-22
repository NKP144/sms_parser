from django.contrib import admin
from .models import *

# Register your models here.


class SMSDataAdmin(admin.ModelAdmin):
    """Класс-редактор для задания параметров представления модели"""
    list_display = ('content', 'time_created')  # Поля, которые выводятся в списке записей


class ParsedMetaDataAdmin(admin.ModelAdmin):
    """Класс-редактор для задания параметров представления модели"""
    list_display = ('sms_generation_time',)  # Поля, которые выводятся в списке записей


admin.site.register(SMSData, SMSDataAdmin)
admin.site.register(ParsedMetaData, ParsedMetaDataAdmin)
