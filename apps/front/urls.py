from django.conf.urls import re_path
from . import views, ajax

urlpatterns = [
    re_path(r'^$', views.overview, name='home'),
    re_path(r'^statistics/?$', views.statistics, name='statistics'),
    re_path(r'^vulnerabilities/?$', views.vulnerabilities, name='vulnerabilities'),
    re_path(r'^search/?$', views.search, name='search'),
    re_path(r'^paging/?$', ajax.paging, name='paging'),
]
