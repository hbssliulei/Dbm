from django.contrib import admin
from models import Game, dbBackup, Assets
# Register your models here.

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('game_name', 'game_cn', '_get_black_list', 'format_datetime', '_is_online')
    search_fields = ('game_cn',)

@admin.register(Assets)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('game', 'ip', 'datetime')
    list_filter = ('game',)

@admin.register(dbBackup)
class dbBackupAdmin(admin.ModelAdmin):
    list_display = ('game', 'ip', 'curdate', 'inc', 'backup_type')
    list_filter = ('game',)
    search_fields = ('game',)

    fieldsets = (
        ('Basic', {
            'fields':('game', 'ip',)
        }),
        ('Advanced', {
            'fields':('backup_type', 'inc'),
            'classes':('collapse',)
        })
    )