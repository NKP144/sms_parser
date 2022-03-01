from django.db import models
from django.urls import reverse

# Create your models here.


class SMSData(models.Model):
    """ Модель хранит данные изи СМС и время её загрузки для обработки """
    content = models.CharField(max_length=160, verbose_name="Содержимое СМС")  # Содержимое СМС
    time_created = models.DateTimeField(auto_now_add=True, verbose_name="Время загрузки для обработки")   # Фиксирует текущее время в момент добавления записи и менятся не будет

    class Meta:
        verbose_name = "СМС"
        verbose_name_plural = "СМС"
        ordering = ['-time_created']


class ParsedMetaData(models.Model):
    """ Модель хранить мета данные из обработанной СМС"""
    sms_generation_time = models.DateTimeField(verbose_name="Время формирования СМС")
    vbat_hi = models.IntegerField(verbose_name="Напряжение батарейки под нагрузкой")
    modem_work_time = models.IntegerField(verbose_name="Время работы модема")
    range_counter = models.IntegerField(verbose_name="Счётчик включений дальномера")
    sms_attempt_counter = models.IntegerField(verbose_name="Счётчик попыток отправки СМС")
    sms_confirmed_counter = models.IntegerField(verbose_name="Счётчик подтвержденных СМС")
    longitude = models.FloatField(verbose_name="Долгота")
    latitude = models.FloatField(verbose_name="Широта")
    vbat_low = models.IntegerField(verbose_name="Напряжение батарейки без нагрузки")
    from_accel = models.BooleanField(default=False, verbose_name="СМС от акселерометра")
    work_from_LSI = models.BooleanField(default=False, verbose_name="Работа от LSI")
    sms = models.OneToOneField(SMSData, on_delete=models.CASCADE, verbose_name="Связанное СМС")

    def get_absolute_url(self):  # Это функция используется в шаблоне для возврата ссылки на элемент из БАЗЫ ДАННЫХ
        # return reverse('parsed_sms', kwargs={'sms_id': self.sms_id})
        return reverse('parsed_sms', kwargs={'metadata_id': self.pk})

    class Meta:
        verbose_name = "Мета данные из СМС"
        verbose_name_plural = "Мета данные из СМС"
        ordering = ['id']


class ParsedMeasureData(models.Model):
    """ Модель хранить данные об измерениях из обработанной СМС"""
    measure_time = models.DateTimeField(verbose_name="Время измерения")
    temperature = models.SmallIntegerField(verbose_name="Температура")
    range = models.SmallIntegerField(verbose_name='Дальномер')
    sms = models.ForeignKey(SMSData, on_delete=models.CASCADE, verbose_name="Связанное СМС")

    # def get_absolute_url(self):
    #     return reverse('parsed_sms', kwargs={'metadata_id': self.pk})

    class Meta:
        verbose_name = "Измерение из СМС"
        verbose_name_plural = "Измерения из СМС"
        ordering = ['-sms_id', 'measure_time']


