from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^packages/?$', views.packages, name='package_list'),
    url(r'^packages/(?P<packageID>\d+)/?$', views.package, name='package_detail'),
    url(r'^packages/add/?$', views.add, name='package_add'),
    url(r'^packages/save/?$', views.save, name='package_save'),
    url(r'^packages/(?P<packageID>\d+)/delete/?$', views.delete, name='package_delete'),
    url(r'^packages/check/?$', views.check, name='package_check'),
    url(r'^packages/(?P<packageID>\d+)/add-version/?$', views.add_version, name='add_package_version'),
    url(r'^packages/(?P<packageID>\d+)/versions/(?P<versionID>\d+)/remove/?$', views.delete_version, name='version_delete'),
]
