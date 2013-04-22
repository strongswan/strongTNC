from django.conf.urls import patterns, include, url
from django.contrib import admin
import settings
import views

admin.autodiscover()

urlpatterns = patterns('',
        url(r'^media/(?P<path>.*)$','django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),

        #Management CRUD views
        url(r'^$', views.overview, name='overview'),
        
        url(r'^overview/?$', views.overview, name='overview'),

        url(r'^groups/?$', views.groups, name='groups'),
        url(r'^groups/(?P<groupID>\d+)/?$', views.group, name='group'),
        url(r'^groups/add/?$', views.group_add, name='group_add'),
        url(r'^groups/save?$', views.group_save, name='group_save'),
        url(r'^groups/(?P<groupID>\d+)/delete/?$', views.group_delete,
            name='group_delete'),

        url(r'^devices/?$', views.devices, name='devices'),
        url(r'^devices/(?P<deviceID>\d+)/?$', views.device, name='device'),
        url(r'^devices/add/?$', views.device_add, name='device_add'),
        url(r'^devices/save?$', views.device_save, name='device_save'),
        url(r'^devices/(?P<deviceID>\d+)/delete/?$', views.device_delete,
            name='device_delete'),

        url(r'^products/?$', views.products, name='products'),
        url(r'^products/(?P<productID>\d+)/?$', views.product, name='product'),
        url(r'^products/add/?$', views.product_add, name='product_add'),
        url(r'^products/save?$', views.product_save, name='product_save'),
        url(r'^products/(?P<productID>\d+)/delete/?$', views.product_delete,
            name='product_delete'),
        
        url(r'^policies/?$', views.policies, name='policies'),
        url(r'^policies/(?P<policyID>\d+)/?$', views.policy, name='policy'),
        url(r'^policies/add/?$', views.policy_add, name='policy_add'),
        url(r'^policies/save?$', views.policy_save, name='policy_save'),
        url(r'^policies/(?P<policyID>\d+)/delete/?$', views.policy_delete,
            name='policy_delete'),
        
        #==============================================

        #IMV API patterns
        url(r'^cmd/start_measurement/?$', views.start_measurement,
            name='start_measurement'),

        url(r'^cmd/end_measurement/?$', views.end_measurement,
            name='end_measurement'),


        #To enable built-in admin-interface:
        url(r'^admin/', include(admin.site.urls)),
        )
