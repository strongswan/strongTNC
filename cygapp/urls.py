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
        url(r'^groups/(?P<groupID>\d+)/delete/?$', views.group_delete,
            name='group_delete'),
        url(r'^groups/add/?$', views.group_add, name='group_add'),
        url(r'^groups/save?$', views.group_save, name='group_save'),

        #==============================================

        #IMV API patterns
        url(r'^cmd/start_measurement/?$', views.start_measurement,
            name='start_measurement'),

        url(r'^cmd/end_measurement/?$', views.end_measurement,
            name='end_measurement'),


        #To enable built-in admin-interface:
        url(r'^admin/', include(admin.site.urls)),
        )
