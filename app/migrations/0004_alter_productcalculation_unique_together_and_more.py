# Generated by Django 4.2.7 on 2024-10-02 20:25

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_alter_calculation_date_created_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='productcalculation',
            unique_together=set(),
        ),
        migrations.AlterField(
            model_name='calculation',
            name='date_created',
            field=models.DateTimeField(default=datetime.datetime(2024, 10, 2, 20, 25, 16, 928317, tzinfo=datetime.timezone.utc), verbose_name='Дата создания'),
        ),
        migrations.AddConstraint(
            model_name='productcalculation',
            constraint=models.UniqueConstraint(fields=('product', 'calculation'), name='unique_productcalculation'),
        ),
    ]
