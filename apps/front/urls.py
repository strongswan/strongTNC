from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns('',
    url(r'^$', views.overview, name='home'),
    url(r'^statistics/?$', views.statistics, name='statistics'),
    url(r'^search/?$', views.search, name='search'),
)
