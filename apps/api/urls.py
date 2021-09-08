# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.conf.urls import re_path, include

from rest_framework import routers

from apps.core.api_views import IdentityViewSet, SessionViewSet, ResultViewSet
from apps.swid.api_views import EventViewSet, EntityViewSet, TagViewSet, TagStatsViewSet, TagAddView
from apps.swid.api_views import SwidMeasurementView, SwidEventsView
from apps.devices.api_views import ProductViewSet, DeviceViewSet
from apps.policies.api_views import PolicyViewSet
from apps.packages.api_views import PackageViewSet, VersionViewSet
from apps.filesystem.api_views import AlgorithmViewSet, DirectoryViewSet, FileViewSet, FileHashViewSet

# Create router
router = routers.DefaultRouter()

# Register resources
router.register(r'identities', IdentityViewSet)
router.register(r'sessions', SessionViewSet)
router.register(r'results', ResultViewSet)
router.register(r'policies', PolicyViewSet)
router.register(r'products', ProductViewSet)
router.register(r'devices', DeviceViewSet)
router.register(r'packages', PackageViewSet)
router.register(r'versions', VersionViewSet)
router.register(r'directories', DirectoryViewSet)
router.register(r'files', FileViewSet)
router.register(r'file-hashes', FileHashViewSet)
router.register(r'algorithms', AlgorithmViewSet)
router.register(r'swid-events', EventViewSet)
router.register(r'swid-entities', EntityViewSet)
router.register(r'swid-tags', TagViewSet)
router.register(r'swid-stats', TagStatsViewSet)

# Generate basic URL configuration
urlpatterns = router.urls

# Register additional endpoints
urlpatterns += [
    # Auth views
    re_path(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    # Add tags
    re_path(r'^swid/add-tags/', TagAddView.as_view(), name='swid-add-tags'),
    re_path(r'^swid/add-tags/\.(?P<format>[a-z0-9]+)', TagAddView.as_view(), name='swid-add-tags'),

    # Register SW ID inventory upload
    re_path(r'^sessions/(?P<pk>[^/]+)/swid-measurement/',
        SwidMeasurementView.as_view(), name='session-swid-measurement'),
    re_path(r'^sessions/(?P<pk>[^/]+)/swid-measurement/\.(?P<format>[a-z0-9]+)',
        SwidMeasurementView.as_view(), name='session-swid-measurement'),

    # Register SW ID events upload
    re_path(r'^sessions/(?P<pk>[^/]+)/swid-events/',
        SwidEventsView.as_view(), name='session-swid-events'),
    re_path(r'^sessions/(?P<pk>[^/]+)/swid-events/\.(?P<format>[a-z0-9]+)',
        SwidEventsView.as_view(), name='session-swid-events'),
]
