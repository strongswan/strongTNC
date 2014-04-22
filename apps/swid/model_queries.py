from tncapp import models as tnc_models


def get_installed_tags_with_time(session_id):
    """
    Return all measured tags upto the given session_id with their first reported time.

    All tags installed by previous sessions are also included

    Args:
        session_id (int):
            The session id
    Returns:
        Tuple (tag, time)
            tag : SWID-Tag
            time: Time the Tag was first measured to be installed
    """
    session = tnc_models.Session.objects.get(pk=session_id)
    device = session.device
    device_sessions = device.sessions.filter(time__lte=session.time).order_by('time')
    tags = []
    tag_set = set()
    for session in device_sessions.all():
        for tag in session.tag_set.all():
            if tag not in tag_set:
                tag_set.add(tag)
                tags.append((tag, session.time))

    return tags