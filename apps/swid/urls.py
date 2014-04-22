from django.conf.urls import patterns, url, include
from . import views

urlpatterns = patterns('',
                       url(r'^regids/$', views.RegidListView.as_view(), name='regid_list'),
                       url(r'^regids/(?P<pk>\d+)/$', views.RegidDetailView.as_view(), name='regid_detail'),
                       url(r'^swid-inventory/(?P<pk>\d+)/$', views.SwidInventoryView.as_view(), name='swid_inventory'),
)