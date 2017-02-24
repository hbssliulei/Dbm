from django.contrib import admin
from models import Game, dbBackup, Assets
# Register your models here.

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('game_name', 'game_cn', 'create_time', '_is_new_project')
    search_fields = ('game_cn',)

@admin.register(Assets)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('game', 'ip', 'datetime')
    list_filter = ('game',)

@admin.register(dbBackup)
class dbBackupAdmin(admin.ModelAdmin):
    list_display = ('game', 'ip', 'curdate', 'backup_type')
    list_filter = ('game',)
    search_fields = ('game',)

    fieldsets = (
        ('Basic', {
            'fields':('game', 'ip',)
        }),
        ('Advanced', {
            'fields':('backup_type',),
            'classes':('collapse',)
        })
    )