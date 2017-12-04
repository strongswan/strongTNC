from django.conf.urls import url
from . import file_views, directory_views, ajax

urlpatterns = [
    url(r'^files/?$', file_views.files, name='file_list'),
    url(r'^files/(?P<fileID>\d+)/?$', file_views.file, name='file_detail'),
    url(r'^files/add/?$', file_views.add, name='file_add'),
    url(r'^files/save/?$', file_views.save, name='file_save'),
    url(r'^files/(?P<fileID>\d+)/delete/?$', file_views.delete, name='file_delete'),
    url(r'^files/autocomplete/?$', ajax.files_autocomplete, name='file_autocomplete'),

    url(r'^file_hashes/(?P<file_hashID>\d+)/delete/?$', file_views.delete_hash, name='filehash_delete'),

    url(r'^directories/?$', directory_views.directories, name='directory_list'),
    url(r'^directories/(?P<directoryID>\d+)/?$', directory_views.directory, name='directory_detail'),
    url(r'^directories/add/?$', directory_views.add, name='directory_add'),
    url(r'^directories/save/?$', directory_views.save, name='directory_save'),
    url(r'^directories/(?P<directoryID>\d+)/delete/?$', directory_views.delete, name='directory_delete'),
    url(r'^directories/check/?$', directory_views.check, name='directory_check'),
    url(r'^directories/autocomplete/?$', ajax.directories_autocomplete, name='directory_autocomplete'),
]
