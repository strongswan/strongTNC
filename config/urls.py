# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from dajaxice.core import dajaxice_autodiscover, dajaxice_config

dajaxice_autodiscover()


# App URLs
urlpatterns = patterns('',
    url(r'', include('apps.front.urls', namespace='front')),
    url(r'', include('apps.core.urls', namespace='core')),
    url(r'', include('apps.auth.urls', namespace='auth')),
    url(r'', include('apps.policies.urls', namespace='policies')),
    url(r'', include('apps.devices.urls', namespace='devices')),
    url(r'', include('apps.packages.urls', namespace='packages')),
    url(r'', include('apps.filesystem.urls', namespace='filesystem')),
    url(r'', include('apps.swid.urls', app_name='swid')),
)

# AJAX URLs
urlpatterns += patterns('',
    url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),
)

# API URLs
urlpatterns += patterns('',
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
)

# Admin URLs. Only in DEBUG mode for now.
if settings.DEBUG:
    admin.autodiscover()
    urlpatterns += patterns('',
        url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
        url(r'^admin/', include(admin.site.urls)),
    )

# Static and media files. This should only be used in DEBUG mode. For live
# deployment, serve your static files directly using the webserver (e.g. Nginx
# or Apache).
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
