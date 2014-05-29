# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import math
from collections import OrderedDict, namedtuple

from django.conf import settings
from django.core.urlresolvers import reverse

from .models import Entity, Tag
from apps.core.models import Session
from apps.devices.models import Device
from apps.front.paging import ProducerFactory

# PAGING PRODUCER

swid_producer_factory = ProducerFactory(Tag, 'unique_id__icontains')

regid_producer_factory = ProducerFactory(Entity, 'regid__icontains')


def entity_swid_list_producer(from_idx, to_idx, filter_query, dynamic_params=None, static_params=None):
    entity_id = dynamic_params['entity_id']
    tag_list = Entity.objects.get(pk=entity_id).tags.all()
    if filter_query:
        tag_list = tag_list.filter(unique_id__icontains=filter_query)
    return tag_list[from_idx:to_idx]


def entity_swid_stat_producer(page_size, filter_query, dynamic_params=None, static_params=None):
    entity_id = dynamic_params['entity_id']
    tag_list = Entity.objects.get(pk=entity_id).tags.all()
    count = tag_list.count()
    if filter_query:
        count = tag_list.filter(unique_id__icontains=filter_query).count()
    return math.ceil(count / page_size)


def swid_inventory_list_producer(from_idx, to_idx, filter_query, dynamic_params, static_params=None):
    if not dynamic_params:
        return []
    session_id = dynamic_params.get('session_id')
    installed_tags = list(get_installed_tags_dict(session_id, filter_query).items())[from_idx:to_idx]

    tags = [
        {
            'added_now': int(session_id) == session.pk,
            'tag': tag,
            'session': session,
            'tag_url': reverse('swid:tag_detail', args=[tag.pk]),
        }
        for tag, session in installed_tags
    ]
    return tags


def swid_inventory_stat_producer(page_size, filter_query, dynamic_params=None, static_params=None):
    if not dynamic_params:
        return 0
    session_id = dynamic_params.get('session_id')
    installed_tags = get_installed_tags_dict(session_id, filter_query)
    return math.ceil(len(installed_tags) / page_size)


def get_installed_tags_dict(session_id, filter_query):
    """
    Return a dict of tags which are installed at the
    point of the given session, furthermore the session in
    which the tag was reported is provided as well.

    Args:
        session_id (int):
            The session to be queried

        filter_query (str):
            Filter the tags (unique_id) by this string

    Returns:
        A dictionary with the reported tag as key and the session in
        which it was reported as value:
        {
            tag: session,
            tag: session,
            ...,
        }

    """
    session = Session.objects.get(pk=session_id)
    installed_tags = Tag.get_installed_tags_with_time(session)
    if filter_query:
        installed_tags = {t: s for t, s in installed_tags.iteritems()
                          if filter_query.lower() in t.unique_id.lower()}
    return installed_tags


def swid_log_list_producer(from_idx, to_idx, filter_query, dynamic_params, static_params=None):
    if not dynamic_params:
        return []
    device_id = dynamic_params.get('device_id')
    from_timestamp = dynamic_params.get('from_timestamp')
    to_timestamp = dynamic_params.get('to_timestamp')

    diffs = get_tag_diffs(device_id, from_timestamp, to_timestamp)[from_idx:to_idx]

    result = OrderedDict()
    for diff in diffs:
        tag = diff.tag
        tag.added = diff.action == '+'
        if diff.session not in result:
            result[diff.session] = [tag]
        else:
            result[diff.session].append(tag)
    return result


def swid_log_stat_producer(page_size, filter_query, dynamic_params=None, static_params=None):
    if not dynamic_params:
        return 0
    device_id = dynamic_params.get('device_id')
    from_timestamp = dynamic_params.get('from_timestamp')
    to_timestamp = dynamic_params.get('to_timestamp')
    diffs = get_tag_diffs(device_id, from_timestamp, to_timestamp)
    return math.ceil(len(diffs) / page_size)


def get_tag_diffs(device_id, from_timestamp, to_timestamp):
    """
    Get differences of installed SWID tags between all sessions of the
    given device in the given timerange (see `session_tag_difference`).
    """
    device = Device.objects.get(pk=device_id)
    sessions = device.get_sessions_in_range(from_timestamp, to_timestamp)

    sessions_with_tags = sessions.filter(tag__isnull=False).distinct().order_by('-time')

    diffs = []
    # diff only possible if more than 1 session is selected
    if len(sessions_with_tags) > 1:
        for i, session in enumerate(sessions_with_tags, start=1):
            if i < len(sessions_with_tags):
                prev_session = sessions_with_tags[i]
                diff = session_tag_difference(session, prev_session)
                diffs.extend(diff)

    return diffs


def session_tag_difference(curr_session, prev_session):
    """
    Calculate the difference of the installed SWID tags between
    the two given sessions.

    Args:
        curr_session (apps.core.models.Session):
            The current session

        prev_session (apps.core.models.Session):
            The session before

    Returns:
        A list of named tuples, consisting of a session object,
        a tag object and an action (str) which is either '+' for
        added or '-' for removed:
            [
                (session: session, action: '+', tag: tag),
                (session: session, action: '-', tag: tag),
                ...,
            ]

    """
    curr_tag_ids = curr_session.tag_set.values_list('id', flat=True).order_by('id')
    prev_tag_ids = prev_session.tag_set.values_list('id', flat=True).order_by('id')

    added_ids = set(curr_tag_ids) - set(prev_tag_ids)
    removed_ids = set(prev_tag_ids) - set(curr_tag_ids)

    added_tags = Tag.objects.filter(id__in=added_ids)
    removed_tags = Tag.objects.filter(id__in=removed_ids)

    differences = []
    DiffEntry = namedtuple('DiffEntry', ['session', 'action', 'tag'])
    for tag in added_tags:
        entry = DiffEntry(curr_session, '+', tag)
        differences.append(entry)

    for tag in removed_tags:
        entry = DiffEntry(curr_session, '-', tag)
        differences.append(entry)

    return differences


# PAGING CONFIGS

regid_list_paging = {
    'template_name': 'front/paging/default_list',
    'list_producer': regid_producer_factory.list(),
    'stat_producer': regid_producer_factory.stat(),
    'url_name': 'swid:regid_detail',
    'page_size': 50,
}

regid_detail_paging = {
    'template_name': 'front/paging/regid_list_tags',
    'list_producer': entity_swid_list_producer,
    'stat_producer': entity_swid_stat_producer,
    'url_name': 'swid:tag_detail',
    'page_size': 50,
}

swid_list_paging = {
    'template_name': 'front/paging/default_list',
    'list_producer': swid_producer_factory.list(),
    'stat_producer': swid_producer_factory.stat(),
    'url_name': 'swid:tag_detail',
    'page_size': 50,
}

swid_inventory_list_paging = {
    'template_name': 'swid/paging/swid_inventory_list',
    'list_producer': swid_inventory_list_producer,
    'stat_producer': swid_inventory_stat_producer,
    'url_name': 'swid:tag_detail',
    'page_size': 50,
}

swid_log_list_paging = {
    'template_name': 'swid/paging/swid_log_list',
    'list_producer': swid_log_list_producer,
    'stat_producer': swid_log_stat_producer,
    'url_name': 'swid:tag_detail',
    'page_size': 50,
}
