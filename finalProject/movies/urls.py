from django.conf.urls import url,include

from . import views

urlpatterns = [
    url(r'admin.html$', views.admin, name='admin'),
    url(r'^$', views.index, name='index'),
    url(r'^newuser.html$', views.get_name, name='userForm'),
    url(r'^initialpicks.html/(?P<id>[0-9]+)/$', views.new_user_movies, name='newUserMovieListForm'),
    url(r'^recommendations.html/(?P<id>[0-9]+)/$', views.recommend_movies, name='recommendations'),
    url(r'^charts/histRated.png$', views.histRated ,name='histRated'),
       url(r'^charts/histGenre1.png$', views.histGenre1 ,name='histGenre1'),
          url(r'^charts/histProd.png$', views.histProd ,name='histProd'),
             url(r'^charts/histYear.png$', views.histYear ,name='histYear'),
]