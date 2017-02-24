#coding:utf-8
from __future__ import unicode_literals

from django.db import models

import datetime
from django.utils import timezone
# Create your models here.

class Game(models.Model):
    game_name = models.CharField("项目标识", max_length=200)
    game_cn = models.CharField("项目中文简称", max_length=200)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)

    def _is_new_project(self):
        return self.create_time >= timezone.now() - datetime.timedelta(days = 30)
    _is_new_project.boolean = True
    _is_new_project.short_description = "最否是新项目"

    def __unicode__(self):
        return self.game_cn

    class Meta:
        db_table = 'game'
        verbose_name = '项目'
        verbose_name_plural = verbose_name

class Assets(models.Model):
    game = models.ForeignKey('Game', verbose_name='项目标识')
    ip = models.GenericIPAddressField("IP")
    datetime = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.ip

    class Meta:
        db_table = 'assets'
        verbose_name = '资产'
        verbose_name_plural = verbose_name

class dbBackup(models.Model):
    game = models.ForeignKey("Game", verbose_name="项目标识")
    ip = models.GenericIPAddressField("IP")
    curdate = models.DateField("最新备份日期", auto_now=True)
    inc = models.CharField("最新备份时间", max_length=8)

    backup_types = (
        (0, '完整备份'),
        (1, '增量备份')
    )

    backup_type = models.SmallIntegerField("备份类型", choices=backup_types)

    def __unicode__(self):
        return self.ip

    class Meta:
        db_table = 'dbBackup'
        verbose_name = 'DB备份'
        verbose_name_plural = verbose_name