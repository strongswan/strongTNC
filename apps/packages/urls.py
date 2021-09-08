from django.conf.urls import re_path
from . import views

urlpatterns = [
    re_path(r'^packages/?$', views.packages, name='package_list'),
    re_path(r'^packages/(?P<packageID>\d+)/?$', views.package, name='package_detail'),
    re_path(r'^packages/add/?$', views.add, name='package_add'),
    re_path(r'^packages/save/?$', views.save, name='package_save'),
    re_path(r'^packages/(?P<packageID>\d+)/delete/?$', views.delete, name='package_delete'),
    re_path(r'^packages/check/?$', views.check, name='package_check'),
    re_path(r'^packages/(?P<packageID>\d+)/add-version/?$', views.add_version, name='add_package_version'),
    re_path(r'^packages/(?P<packageID>\d+)/versions/(?P<versionID>\d+)/remove/?$', views.delete_version, name='version_delete'),
]
