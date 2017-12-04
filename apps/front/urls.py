from django.conf.urls import url
from . import views, ajax

urlpatterns = [
    url(r'^$', views.overview, name='home'),
    url(r'^statistics/?$', views.statistics, name='statistics'),
    url(r'^vulnerabilities/?$', views.vulnerabilities, name='vulnerabilities'),
    url(r'^search/?$', views.search, name='search'),
    url(r'^paging/?$', ajax.paging, name='paging'),
]
