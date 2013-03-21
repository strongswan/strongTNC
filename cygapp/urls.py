from django.conf.urls.defaults import patterns, url
from django.views.generic import DetailView, ListView
from cygapp.models import *
import settings
import views

urlpatterns = patterns('',
        url(r'^$', views.index, name='index'),

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
        )
