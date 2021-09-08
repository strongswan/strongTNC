from django.conf.urls import re_path
from . import file_views, directory_views, ajax

urlpatterns = [
    re_path(r'^files/?$', file_views.files, name='file_list'),
    re_path(r'^files/(?P<fileID>\d+)/?$', file_views.file, name='file_detail'),
    re_path(r'^files/add/?$', file_views.add, name='file_add'),
    re_path(r'^files/save/?$', file_views.save, name='file_save'),
    re_path(r'^files/(?P<fileID>\d+)/delete/?$', file_views.delete, name='file_delete'),
    re_path(r'^files/autocomplete/?$', ajax.files_autocomplete, name='file_autocomplete'),

    re_path(r'^file_hashes/(?P<file_hashID>\d+)/delete/?$', file_views.delete_hash, name='filehash_delete'),

    re_path(r'^directories/?$', directory_views.directories, name='directory_list'),
    re_path(r'^directories/(?P<directoryID>\d+)/?$', directory_views.directory, name='directory_detail'),
    re_path(r'^directories/add/?$', directory_views.add, name='directory_add'),
    re_path(r'^directories/save/?$', directory_views.save, name='directory_save'),
    re_path(r'^directories/(?P<directoryID>\d+)/delete/?$', directory_views.delete, name='directory_delete'),
    re_path(r'^directories/check/?$', directory_views.check, name='directory_check'),
    re_path(r'^directories/autocomplete/?$', ajax.directories_autocomplete, name='directory_autocomplete'),
]
