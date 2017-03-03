from django.conf.urls import url

from god import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^get_db_backup/', views.get_db_backup_data, name='get_db_backup'),
    url(r'^get_game_backup/(?P<game>\w+)/', views.get_game_backup, name='get_game_backup'),
    url(r'^test/', views.test),
]