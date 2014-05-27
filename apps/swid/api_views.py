# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from rest_framework import viewsets, views, status
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from lxml.etree import XMLSyntaxError

from . import utils, serializers

from .models import Entity, Tag
from apps.core.models import Session


class EntityViewSet(viewsets.ReadOnlyModelViewSet):
    model = Entity
    serializer_class = serializers.EntitySerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    model = Tag
    serializer_class = serializers.TagSerializer
    filter_fields = ('package_name', 'version', 'unique_id')


class TagAddView(views.APIView):
    """
    Read the submitted SWID XML tags, parse them and store them into the
    database.

    The SWID tags should be submitted in a JSON formatted list, with the
    ``Content-Type`` header set to ``application/json; charset=utf-8``.

    """
    parser_classes = (JSONParser,)  # Only JSON data is supported

    def post(self, request, format=None):
        # Validate request data
        tags = request.DATA
        if not isinstance(tags, list):
            data = {
                'status': 'error',
                'message': 'Request body must be JSON formatted list of XML tags.',
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        # Process tags
        stats = {'added': 0, 'replaced': 0}
        for tag in tags:
            try:
                tag, replaced = utils.process_swid_tag(tag)
            except XMLSyntaxError:
                data = {'status': 'error', 'message': 'Invalid XML'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            except ValueError as e:
                data = {'status': 'error', 'message': unicode(e)}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Update stats
                if replaced:
                    stats['replaced'] += 1
                else:
                    stats['added'] += 1

        data = {
            'status': 'success',
            'message': 'Added {0[added]} SWID tags, replaced {0[replaced]} SWID tags.'.format(stats),
        }
        return Response(data, status=status.HTTP_200_OK)


class SwidMeasurementView(views.APIView):
    """
    Link the given software-ids with the current session.

    If no corresponding tag is available for one or more software-ids, return
    these software-ids with HTTP status code 412 Precondition failed.

    This view is defined on a session detail page. The ``pk`` argument is the
    session ID.

    """
    def post(self, request, pk, format=None):
        software_ids = request.DATA
        missing_tags = []
        found_tags = Tag.objects.filter(software_id__in=software_ids)

        # Look for matching tags
        found_software_ids = [t.software_id for t in found_tags]
        for software_id in software_ids:
            if software_id not in found_software_ids:
                missing_tags.append(software_id)

        if missing_tags:
            # Some tags are missing
            return Response(data=missing_tags, status=status.HTTP_412_PRECONDITION_FAILED)
        else:
            # All tags are available: link them with a session
            try:
                session = Session.objects.get(pk=pk)
            except Session.DoesNotExist:
                data = {'status': 'error', 'message': 'Session with id "%s" not found.' % pk}
                return Response(data=data, status=status.HTTP_404_NOT_FOUND)
            utils.chunked_bulk_create(session.tag_set, found_tags, 980)
            return Response(data=[], status=status.HTTP_200_OK)
