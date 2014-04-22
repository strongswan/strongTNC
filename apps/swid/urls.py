from django.conf.urls import patterns, url, include
from . import views

urlpatterns = patterns('',
    url(r'^regids/$', views.RegidListView.as_view(), name='regid_list'),
    url(r'^regids/(?P<pk>\d+)/$', views.RegidDetailView.as_view(), name='regid_detail'),
    url(r'^swid-tags/$', views.SwidTagListView.as_view(), name='swid_tag_list'),
    url(r'^swid-tags/(?P<pk>\d+)/$', views.SwidTagDetailView.as_view(), name='swid_tag_detail'),
)
