# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from rest_framework import viewsets, views, status
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from lxml.etree import XMLSyntaxError

from apps.swid import utils
from . import models
from . import serializers


class EntityViewSet(viewsets.ReadOnlyModelViewSet):
    model = models.Entity
    serializer_class = serializers.EntitySerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    model = models.Tag
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

    def post(self, request):
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
