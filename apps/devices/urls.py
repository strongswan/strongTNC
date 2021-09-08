from django.conf.urls import re_path
from . import device_views, group_views, product_views

urlpatterns = [
    re_path(r'^devices/?$', device_views.devices, name='device_list'),
    re_path(r'^devices/(?P<deviceID>\d+)/?$', device_views.device, name='device_detail'),
    re_path(r'^devices/add/?$', device_views.add, name='device_add'),
    re_path(r'^devices/save/?$', device_views.save, name='device_save'),
    re_path(r'^devices/(?P<deviceID>\d+)/delete/?$', device_views.delete, name='device_delete'),
    re_path(r'^devices/(?P<device_id>\d+)/toggle/?$', device_views.toggle_trusted, name='device_toggle_trusted'),
    re_path(r'^devices/(?P<device_id>\d+)/toggle/?$', device_views.toggle_inactive, name='device_toggle_inactive'),
    re_path(r'^devices/check/?$', device_views.check, name='device_check'),

    re_path(r'^devices/(?P<deviceID>\d+)/report/?$', device_views.report, name='device_report'),

    re_path(r'^events/(?P<eventID>\d+)/?$', device_views.event, name='event_detail'),
    re_path(r'^sessions/(?P<sessionID>\d+)/?$', device_views.session, name='session_detail'),

    re_path(r'^groups/?$', group_views.groups, name='group_list'),
    re_path(r'^groups/(?P<groupID>\d+)/?$', group_views.group, name='group_detail'),
    re_path(r'^groups/add/?$', group_views.add, name='group_add'),
    re_path(r'^groups/save/?$', group_views.save, name='group_save'),
    re_path(r'^groups/(?P<groupID>\d+)/delete/?$', group_views.delete, name='group_delete'),
    re_path(r'^groups/check/?$', group_views.check, name='group_check'),

    re_path(r'^products/?$', product_views.products, name='product_list'),
    re_path(r'^products/(?P<productID>\d+)/?$', product_views.product, name='product_detail'),
    re_path(r'^products/add/?$', product_views.add, name='product_add'),
    re_path(r'^products/save/?$', product_views.save, name='product_save'),
    re_path(r'^products/(?P<productID>\d+)/delete/?$', product_views.delete, name='product_delete'),
    re_path(r'^products/check/?$', product_views.check, name='product_check'),
]
