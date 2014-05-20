# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.conf.urls import url, patterns, include

from rest_framework import routers

from apps.core.api_views import IdentityViewSet, SessionViewSet
from apps.swid.api_views import EntityViewSet, TagViewSet, TagAddView


# Create router
router = routers.DefaultRouter()

# Register resources
router.register(r'identities', IdentityViewSet)
router.register(r'sessions', SessionViewSet)
router.register(r'swid-entities', EntityViewSet)
router.register(r'swid-tags', TagViewSet)

# Generate URL configuration
urlpatterns = router.urls


# API URLs
urlpatterns += patterns('',
    url(r'^swid/add-tags/', TagAddView.as_view(), name='swid-add-tags'),
)
