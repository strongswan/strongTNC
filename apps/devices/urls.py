from django.conf.urls import patterns, url
from . import device_views, group_views, product_views

urlpatterns = patterns('',
    url(r'^devices/?$', device_views.devices, name='device_list'),
    url(r'^devices/(?P<deviceID>\d+)/?$', device_views.device, name='device_detail'),
    url(r'^devices/add/?$', device_views.add, name='device_add'),
    url(r'^devices/save/?$', device_views.save, name='device_save'),
    url(r'^devices/(?P<deviceID>\d+)/delete/?$', device_views.delete, name='device_delete'),
    url(r'^devices/(?P<device_id>\d+)/toggle/?$', device_views.toggle_trusted, name='device_toggle_trusted'),
    url(r'^devices/check/?$', device_views.check, name='device_check'),

    url(r'^devices/(?P<deviceID>\d+)/report/?$', device_views.report, name='device_report'),

    url(r'^events/(?P<eventID>\d+)/?$', device_views.event, name='event_detail'),
    url(r'^sessions/(?P<sessionID>\d+)/?$', device_views.session, name='session_detail'),

    url(r'^groups/?$', group_views.groups, name='group_list'),
    url(r'^groups/(?P<groupID>\d+)/?$', group_views.group, name='group_detail'),
    url(r'^groups/add/?$', group_views.add, name='group_add'),
    url(r'^groups/save/?$', group_views.save, name='group_save'),
    url(r'^groups/(?P<groupID>\d+)/delete/?$', group_views.delete, name='group_delete'),
    url(r'^groups/check/?$', group_views.check, name='group_check'),

    url(r'^products/?$', product_views.products, name='product_list'),
    url(r'^products/(?P<productID>\d+)/?$', product_views.product, name='product_detail'),
    url(r'^products/add/?$', product_views.add, name='product_add'),
    url(r'^products/save/?$', product_views.save, name='product_save'),
    url(r'^products/(?P<productID>\d+)/delete/?$', product_views.delete, name='product_delete'),
    url(r'^products/check/?$', product_views.check, name='product_check'),

)
