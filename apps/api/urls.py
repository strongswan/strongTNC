# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.conf.urls import url, patterns, include

from rest_framework import routers

from apps.core.api_views import IdentityViewSet, SessionViewSet
from apps.swid.api_views import EntityViewSet, TagViewSet, TagAddView, SwidMeasurementView


# Create router
router = routers.DefaultRouter()

# Register resources
router.register(r'identities', IdentityViewSet)
router.register(r'sessions', SessionViewSet)
router.register(r'swid-entities', EntityViewSet)
router.register(r'swid-tags', TagViewSet)

# Generate basic URL configuration
urlpatterns = router.urls

# Register additional endpoints
urlpatterns += patterns('',
    # Auth views
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    # Add tags
    url(r'^swid/add-tags/', TagAddView.as_view(), name='swid-add-tags'),
    url(r'^swid/add-tags/\.(?P<format>[a-z0-9]+)', TagAddView.as_view(), name='swid-add-tags'),

    # Register measurement
    url(r'^sessions/(?P<pk>[^/]+)/swid-measurement/',
        SwidMeasurementView.as_view(), name='session-swid-measurement'),
    url(r'^sessions/(?P<pk>[^/]+)/swid-measurement/\.(?P<format>[a-z0-9]+)',
        SwidMeasurementView.as_view(), name='session-swid-measurement'),
)
