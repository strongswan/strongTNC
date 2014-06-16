# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from rest_framework import viewsets, views, status
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from lxml.etree import XMLSyntaxError

from . import utils, serializers

from .models import Entity, Tag, TagStats
from apps.core.models import Session
from apps.api.utils import make_message


class EntityViewSet(viewsets.ReadOnlyModelViewSet):
    model = Entity
    serializer_class = serializers.EntitySerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    model = Tag
    serializer_class = serializers.TagSerializer
    filter_fields = ('package_name', 'version', 'unique_id')


def validate_data_param(request, list_name):
    """
    Validate data for API views that expect a data=[] like parameter.

    If validation fails, a ValueError is raised, with the response as exception
    message. Otherwise, the list is returned.

    """
    if hasattr(request.DATA, 'getlist'):
        items = request.DATA.getlist('data')
    elif hasattr(request.DATA, 'get'):
        items = request.DATA.get('data')
    else:
        response = make_message('Missing "data" parameter', status.HTTP_400_BAD_REQUEST)
        raise ValueError(response)
    if items is None:
        response = make_message('Missing "data" parameter', status.HTTP_400_BAD_REQUEST)
        raise ValueError(response)
    if not items:
        response = make_message('No %s submitted' % list_name, status.HTTP_400_BAD_REQUEST)
        raise ValueError(response)
    if not isinstance(items, list):
        msg = 'The submitted "data" parameter does not contain a list'
        response = make_message(msg, status.HTTP_400_BAD_REQUEST)
        raise ValueError(response)
    return items


class TagAddView(views.APIView):
    """
    Read the submitted SWID XML tags, parse them and store them into the
    database.

    You can either send data to this endpoint in
    `application/x-www-form-urlencoded` encoding

        data='tag-xml-1'&data='tag-xml-2'&data='tag-xml-3'

    ...or you can use `application/json` encoding:

        {"data": ["tag-xml-1", "tag-xml-2", "tag-xml-3"]}

    """
    parser_classes = (JSONParser,)  # Only JSON data is supported

    def post(self, request, format=None):
        try:
            tags = validate_data_param(request, 'SWID tags')
        except ValueError as e:
            return e.message

        # Process tags
        stats = {'added': 0, 'replaced': 0}
        for tag in tags:
            try:
                tag, replaced = utils.process_swid_tag(tag)
            except XMLSyntaxError:
                return make_message('Invalid XML', status.HTTP_400_BAD_REQUEST)
            except ValueError as e:
                return make_message(unicode(e), status.HTTP_400_BAD_REQUEST)
            else:
                # Update stats
                if replaced:
                    stats['replaced'] += 1
                else:
                    stats['added'] += 1

        msg = 'Added {0[added]} SWID tags, replaced {0[replaced]} SWID tags.'.format(stats)
        return make_message(msg, status.HTTP_200_OK)


class SwidMeasurementView(views.APIView):
    """
    Link the given software-ids with the current session.

    If no corresponding tag is available for one or more software-ids, return
    these software-ids with HTTP status code 412 Precondition failed.

    This view is defined on a session detail page. The `pk` argument is the
    session ID.

    You can either send data to this endpoint in `application/x-www-form-urlencoded` encoding

        data='software-id-1'&data='software-id-2'&data='software-id-n'

    ...or you can use `application/json` encoding:

        {"data": ["software-id-1", "software-id-2", "software-id-n"]}

    """
    def post(self, request, pk, format=None):
        try:
            software_ids = validate_data_param(request, 'software IDs')
        except ValueError as e:
            return e.message

        found_tag_qs = Tag.objects.values_list('software_id', 'pk')
        found_tags = dict(utils.chunked_filter_in(found_tag_qs, 'software_id', software_ids, 980))

        # Look for matching tags
        missing_tags = []
        for software_id in software_ids:
            if software_id not in found_tags:
                missing_tags.append(software_id)

        if missing_tags:
            # Some tags are missing
            return Response(data=missing_tags, status=status.HTTP_412_PRECONDITION_FAILED)
        else:
            # All tags are available: link them with a session
            try:
                session = Session.objects.get(pk=pk)
            except Session.DoesNotExist:
                msg = 'Session with id "%s" not found' % pk
                return make_message(msg, status.HTTP_404_NOT_FOUND)
            utils.chunked_bulk_add(session.tag_set, found_tags.values(), 980)

            # Update tag stats
            # Also possible with signaling https://docs.djangoproject.com/en/dev/ref/signals/#m2m-changed
            utils.update_tag_stats(session, found_tags.values())

            return Response(data=[], status=status.HTTP_200_OK)
