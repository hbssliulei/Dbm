# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('god', '0005_auto_20170303_1343'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dbbackup',
            name='ip',
            field=models.ForeignKey(verbose_name='IP', to='god.Assets'),
        ),
    ]
