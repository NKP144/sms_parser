# Generated by Django 4.0.2 on 2022-02-22 19:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parser_sms', '0008_alter_parsedmeasuredata_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='parsedmeasuredata',
            options={'ordering': ['-sms_id', 'measure_time'], 'verbose_name': 'Измерение из СМС', 'verbose_name_plural': 'Измерения из СМС'},
        ),
    ]
