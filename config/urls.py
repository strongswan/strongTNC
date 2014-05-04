# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin

# App URLs
urlpatterns = patterns('',
    url(r'', include('tncapp.urls')),
    url(r'', include('apps.devices.urls', namespace='devices')),
    url(r'', include('apps.packages.urls', namespace='packages')),
    url(r'', include('apps.filesystem.urls', namespace='filesystem')),
    url(r'', include('apps.swid.urls', app_name='swid')),
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
    urlpatterns += patterns('',
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
                {'document_root': settings.STATIC_ROOT, 'show_indexes': False}),
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
                {'document_root': settings.MEDIA_ROOT, 'show_indexes': False}),
    )
