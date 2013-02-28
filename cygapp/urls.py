from django.conf.urls.defaults import patterns, url
from django.views.generic import DetailView, ListView
from cygapp.models import File, FileHash
import views

urlpatterns = patterns('',
        url(r'^$', views.index, name='index'),
        )
