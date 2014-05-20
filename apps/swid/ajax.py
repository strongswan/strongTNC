# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import json

from dajaxice.decorators import dajaxice_register

from apps.swid.models import Tag
from apps.core.models import Session


@dajaxice_register()
def tags_for_session(request, session_id):
    session = Session.objects.get(pk=session_id)
    installed_tags = Tag.get_installed_tags_with_time(session)
    tags = [
        {
            'name': tag.package_name,
            'version': tag.version,
            'unique-id': tag.unique_id,
            'installed': session.time.strftime('%b %d %H:%M:%S %Y'),
            'session-id': session.pk,
        }
        for tag, session in installed_tags
    ]
    data = {'swid-tag-count': len(tags), 'swid-tags': tags}
    return json.dumps(data)
