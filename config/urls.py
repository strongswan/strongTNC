# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.conf import settings
from django.conf.urls import include, re_path
from django.urls import path
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


# App URLs
urlpatterns = [
    re_path(r'', include(('apps.front.urls', 'front'), namespace='front')),
    re_path(r'', include(('apps.core.urls', 'core'), namespace='core')),
    re_path(r'', include(('apps.authentication.urls', 'authentication'), namespace='authentication')),
    re_path(r'', include(('apps.policies.urls', 'policies'), namespace='policies')),
    re_path(r'', include(('apps.devices.urls', 'devices'), namespace='devices')),
    re_path(r'', include(('apps.packages.urls', 'packages'), namespace='packages')),
    re_path(r'', include(('apps.filesystem.urls', 'filesystem'), namespace='filesystem')),
    re_path(r'', include(('apps.swid.urls', 'swid'), namespace='swid')),
    re_path(r'', include(('apps.tpm.urls', 'tpm'), namespace='tpm')),
]

# API URLs
urlpatterns += [
    # Warning: API URLs are not namespaced. The feature is still in the works:
    # github.com/tomchristie/django-rest-framework/pull/1143
    #
    # Note: If there will be a version 2 of the API in the future, versioning
    # should probably be done via Accept-header.
    re_path(r'^api/', include('apps.api.urls')),
]

# Admin URLs
urlpatterns += [
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),
]

# Static and media files. This should only be used in DEBUG mode. For live
# deployment, serve your static files directly using the webserver (e.g. Nginx
# or Apache).
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
