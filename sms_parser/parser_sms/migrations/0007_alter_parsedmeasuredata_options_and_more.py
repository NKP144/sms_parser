# Generated by Django 4.0.2 on 2022-02-22 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parser_sms', '0006_parsedmeasuredata'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='parsedmeasuredata',
            options={'ordering': ['sms_id'], 'verbose_name': 'Измерение из СМС', 'verbose_name_plural': 'Измерения из СМС'},
        ),
        migrations.AlterField(
            model_name='parsedmeasuredata',
            name='range',
            field=models.SmallIntegerField(verbose_name='Дальномер'),
        ),
        migrations.AlterField(
            model_name='parsedmeasuredata',
            name='temperature',
            field=models.SmallIntegerField(verbose_name='Температура'),
        ),
    ]
