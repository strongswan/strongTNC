from django.conf.urls import patterns, include, url
from django.views.generic import DetailView, ListView
from django.contrib import admin
from cygapp.models import *
import settings
import views

admin.autodiscover()

urlpatterns = patterns('',
        #Management CRUD views
        url(r'^$', views.index, name='index'),
        
        url(r'^overview/?$', views.overview, name='overview'),

        url(r'^groups/?$', views.groups, name='groups'),
        
        url(r'^carousel/?$', views.carousel, name='carousel'),

        url(r'^media/(?P<path>.*)$','django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),

        url(r'^files/?$', 
            ListView.as_view(
                queryset=File.objects.order_by('name'),
                context_object_name = 'flist',
                template_name = 'cygapp/files.html'),
            name='files'),

        url(r'^files/hashes/?$', views.fileshashes, name='fileshashes'),

        url(r'^files/hashes/json/?$', views.fileshashesjson,
            name='fileshashesjson'),

        url(r'^files/(?P<pk>\d+)/?$',
            DetailView.as_view(
                model=File,
                template_name='cygapp/file.html'),
            name='file'),

        url(r'^files/(?P<fileid>\d+)/edit/?$', views.fileedit,
            name='fileedit'),
        url(r'^files/(?P<fileid>\d+)/hashes/?$', views.filehashes,
            name='filehashes'),

        url(r'^files/(?P<fileid>\d+)/json/?$', views.filejson,
            name='filejson'),

        url(r'^files/(?P<fileid>\d+)/hashes/json/?$', views.filehashesjson,
            name='filehashesjson'),

        #IMV API patterns
        url(r'^cmd/start_measurement/?$', views.startMeasurement,
            name='start_measurement'),

        url(r'^cmd/finish_measurement/?$', views.finishMeasurement,
            name='finish_measurement'),


        #To enable built-in admin-interface:
        url(r'^admin/', include(admin.site.urls)),
        )
