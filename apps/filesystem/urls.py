from django.conf.urls import patterns, url
from . import file_views, directory_views

urlpatterns = patterns('',
    url(r'^files/?$', file_views.files, name='file_list'),
    url(r'^files/(?P<fileID>\d+)/?$', file_views.file, name='file_detail'),
    url(r'^files/save/?$', file_views.save, name='file_save'),
    url(r'^files/(?P<fileID>\d+)/delete/?$', file_views.delete, name='file_delete'),

    url(r'^file_hashes/(?P<file_hashID>\d+)/delete/?$', file_views.delete_hash, name='filehash_delete'),

    url(r'^directories/?$', directory_views.directories, name='directory_list'),
    url(r'^directories/(?P<directoryID>\d+)/?$', directory_views.directory, name='directory_detail'),
    url(r'^directories/add/?$', directory_views.add, name='directory_add'),
    url(r'^directories/save/?$', directory_views.save, name='directory_save'),
    url(r'^directories/(?P<directoryID>\d+)/delete/?$', directory_views.delete, name='directory_delete'),
)
