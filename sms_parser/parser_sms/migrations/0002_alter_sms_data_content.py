# Generated by Django 4.0.2 on 2022-02-11 11:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parser_sms', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sms_data',
            name='content',
            field=models.CharField(max_length=160, verbose_name='Содержимое СМС'),
        ),
    ]
