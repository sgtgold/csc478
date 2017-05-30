from django.conf.urls import url,include

from . import views

urlpatterns = [
    url(r'admin.html$', views.admin, name='admin'),
    url(r'^$', views.index, name='index'),
    url(r'^newuser.html$', views.get_name, name='userForm'),
    url(r'^charts/histRated.png$', views.histRated ,name='histRated'),
]