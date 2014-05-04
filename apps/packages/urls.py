from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns('',
    url(r'^packages/?$', views.packages, name='package_list'),
    url(r'^packages/(?P<packageID>\d+)/?$', views.package, name='package_detail'),
    url(r'^packages/add/?$', views.add, name='package_add'),
    url(r'^packages/save/?$', views.save, name='package_save'),
    url(r'^packages/(?P<packageID>\d+)/delete/?$', views.delete, name='package_delete'),
    url(r'^packages/check/?$', views.check, name='package_check'),

    url(r'^versions/(?P<versionID>\d+)/toggle/?$', views.toggle_version, name='package_toggle_version'),
)
