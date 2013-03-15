from django.conf.urls.defaults import patterns, url
from django.views.generic import DetailView, ListView
#from cygapp.models import File, FileHash
import views

urlpatterns = patterns('',
        url(r'^$', views.index, name='index'),
        url(r'^files/?$', views.files, name='files'),
        url(r'^files/hashes/?$', views.fileshashes, name='fileshashes'),
        url(r'^files/hashes/json/?$', views.fileshashesjson, name='fileshashesjson'),
        url(r'^files/(?P<fileid>\d+)/?$', views.file, name='file'),
        url(r'^files/(?P<fileid>\d+)/edit/?$', views.fileedit, name='fileedit'),
        url(r'^files/(?P<fileid>\d+)/hashes/?$', views.filehashes, name='filehashes'),
        url(r'^files/(?P<fileid>\d+)/json/?$', views.filejson, name='filejson'),
        url(r'^files/(?P<fileid>\d+)/hashes/json/?$', views.filehashesjson, name='filehashesjson'),
        )
