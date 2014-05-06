# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.conf.urls import url, patterns, include

from rest_framework import routers

from . import views


# Create router
router = routers.DefaultRouter()

# Register resources
router.register(r'swid-entities', views.EntityViewSet)
router.register(r'swid-tags', views.TagViewSet)

# Generate URL configuration
urlpatterns = router.urls


# API URLs
urlpatterns += patterns('',
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
)
