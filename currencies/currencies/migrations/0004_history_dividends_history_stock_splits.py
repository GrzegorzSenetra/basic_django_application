# Generated by Django 4.2.7 on 2023-11-03 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('currencies', '0003_currency_rate'),
    ]

    operations = [
        migrations.AddField(
            model_name='history',
            name='dividends',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='history',
            name='stock_splits',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]