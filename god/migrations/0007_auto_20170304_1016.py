# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('god', '0006_auto_20170304_1000'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dbbackup',
            name='inc',
            field=models.CharField(max_length=8, verbose_name='\u5907\u4efd\u65f6\u95f4'),
        ),
        migrations.AlterField(
            model_name='dbbackup',
            name='ip',
            field=models.GenericIPAddressField(verbose_name='IP'),
        ),
    ]
