from django.conf.urls import url

from god import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^test/', views.test),
]