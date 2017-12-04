from django.conf.urls import url
from . import views, ajax

urlpatterns = [
    url(r'^regids/$', views.RegidListView.as_view(), name='regid_list'),
    url(r'^regids/(?P<pk>\d+)/$', views.RegidDetailView.as_view(), name='regid_detail'),
    url(r'^swid-tags/$', views.SwidTagListView.as_view(), name='tag_list'),
    url(r'^swid-tags/(?P<pk>\d+)/$', views.SwidTagDetailView.as_view(), name='tag_detail'),
    url(r'^swid-inventory/(?P<pk>\d+)/$', views.SwidInventoryView.as_view(), name='inventory'),
    url(r'^swid-inventory/stats/$', ajax.get_tag_inventory_stats, name='tag_inventory_stats'),
    url(r'^swid-log/(?P<pk>\d+)/$', views.SwidLogView.as_view(), name='log'),
    url(r'^swid-log/stats/$', ajax.get_tag_log_stats, name='tag_log_stats'),
    url(r'^session-info/$', ajax.session_info, name='session_info'),
]
