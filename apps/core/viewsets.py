# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from . import models
from apps.swid import models as swid_models
from apps.core import models as core_models
from . import serializers


class IdentityViewSet(viewsets.ReadOnlyModelViewSet):
    model = models.Identity
    serializer_class = serializers.IdentitySerializer


class SessionViewSet(viewsets.ReadOnlyModelViewSet):
    model = models.Session
    serializer_class = serializers.SessionSerializer

    @action()
    def swid_measurement(self, request, pk=None):
        """"
        Link the given software-ids with the current session.
        If no corresponding tag is available for one or more software-ids, return these software-ids
        with HTTP status code 412 Precondition failed.

        """
        software_ids = request.DATA
        found_tags = {}
        missing_tags = []

        # look for matching tags
        for tag in swid_models.Tag.objects.all():
            ids = tag.get_software_ids()
            for software_id in software_ids:
                if software_id in ids:
                    found_tags[software_id] = tag

        for software_id in software_ids:
            if software_id not in found_tags:
                missing_tags.append(software_id)

        # not all tags for the given software-ids are available, client should create them first
        if missing_tags:
            return Response(data=missing_tags, status=status.HTTP_412_PRECONDITION_FAILED)

        # all tags are available; link them with a session
        else:
            session = core_models.Session.objects.get(pk=pk)
            session.tag_set.add(*found_tags.values())
            session.save()
            return Response()
