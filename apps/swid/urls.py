from django.conf.urls import re_path
from . import views, ajax

urlpatterns = [
    re_path(r'^regids/$', views.RegidListView.as_view(), name='regid_list'),
    re_path(r'^regids/(?P<pk>\d+)/$', views.RegidDetailView.as_view(), name='regid_detail'),
    re_path(r'^swid-tags/$', views.SwidTagListView.as_view(), name='tag_list'),
    re_path(r'^swid-tags/(?P<pk>\d+)/$', views.SwidTagDetailView.as_view(), name='tag_detail'),
    re_path(r'^swid-inventory/(?P<pk>\d+)/$', views.SwidInventoryView.as_view(), name='inventory'),
    re_path(r'^swid-inventory/stats$', ajax.get_tag_inventory_stats, name='tag_inventory_stats'),
    re_path(r'^swid-log/(?P<pk>\d+)/$', views.SwidLogView.as_view(), name='log'),
    re_path(r'^swid-log/stats$', ajax.get_tag_log_stats, name='tag_log_stats'),
    re_path(r'^session-info$', ajax.session_info, name='session_info'),
]
