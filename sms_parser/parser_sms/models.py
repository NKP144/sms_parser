from django.db import models

# Create your models here.


class SMS_data(models.Model):
    content = models.TextField(verbose_name="Содержимое СМС")  # Содержимое СМС
    time_created = models.DateTimeField(auto_now_add=True, verbose_name="Время загрузки для обработки")   # Фиксирует текущее время в момент добавления записи и менятся не будет

    class Meta:
        verbose_name = "СМС"
        verbose_name_plural = "СМС"
        ordering = ['time_created']
