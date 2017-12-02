from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.overview, name='home'),
    url(r'^statistics/?$', views.statistics, name='statistics'),
    url(r'^vulnerabilities/?$', views.vulnerabilities, name='vulnerabilities'),
    url(r'^search/?$', views.search, name='search'),
]
