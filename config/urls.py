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
    url(r'', include('apps.swid.urls', namespace='swid')),
    url(r'', include('apps.tpm.urls', namespace='tpm')),
)

# AJAX URLs
urlpatterns += patterns('',
    url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),
)

# API URLs
urlpatterns += patterns('',
    # Warning: API URLs are not namespaced. The feature is still in the works:
    # github.com/tomchristie/django-rest-framework/pull/1143
    #
    # Note: If there will be a version 2 of the API in the future, versioning
    # should probably be done via Accept-header.
    url(r'^api/', include('apps.api.urls')),
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
