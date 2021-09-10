# -*- coding: utf-8 -*-
"""
Tests for `swid` app.
"""
from __future__ import print_function, division, absolute_import, unicode_literals

from datetime import timedelta

from django.utils import timezone
from django.utils.dateformat import format

import pytest
from model_bakery import baker

from apps.core.models import Session, WorkItem
from apps.core.types import WorkItemType
from apps.swid.models import Tag, EntityRole, Entity, TagStats
from apps.filesystem.models import File, Directory
from apps.swid import utils
from apps.swid.paging import swid_inventory_list_producer, swid_log_list_producer, \
    swid_inventory_stat_producer

### FIXTURES ###

@pytest.fixture
def swidtag(request, transactional_db):
    """
    Create and return a apps.swid.models.Tag instance based on the specified file.

    This requires the test using this fixture to be parametrized with a
    'filename' argument that specifies the filename of the SWID tag test file
    inside `tests/test_tags/`.

    """
    filename = request.getfixturevalue('filename')
    with open('tests/test_tags/%s' % filename, 'r') as f:
        tag_xml = f.read()
        return utils.process_swid_tag(tag_xml, allow_tag_update=True)[0]


@pytest.fixture
def session(transactional_db):
    test_session = baker.make(Session, time=timezone.now())
    workitem = baker.make(WorkItem, type=WorkItemType.SWIDT,
                          session=test_session)

    with open('tests/test_tags/multiple-swid-tags.txt', 'r') as f:
        workitem.result = f.read()
        workitem.save()

    return test_session


### SWID XML PROCESSING TESTS ###

@pytest.mark.parametrize(['filename', 'package_name'], [
    ('strongswan.short.swidtag', 'strongswan'),
    ('strongswan.full.swidtag', 'strongswan'),
    ('cowsay.short.swidtag', 'cowsay'),
    ('cowsay.full.swidtag', 'cowsay'),
    ('strongswan-tnc-imcvs.short.swidtag', 'strongswan-tnc-imcvs'),
    ('strongswan-tnc-imcvs.full.swidtag', 'strongswan-tnc-imcvs'),
])
def test_tag_name(swidtag, filename, package_name):
    assert swidtag.package_name == package_name


@pytest.mark.parametrize(['filename', 'unique_id'], [
    ('strongswan.short.swidtag', 'debian_7.4-x86_64-strongswan-4.5.2-1.5+deb7u3'),
    ('strongswan.full.swidtag', 'debian_7.4-x86_64-strongswan-4.5.2-1.5+deb7u3'),
    ('cowsay.short.swidtag', 'debian_7.4-x86_64-cowsay-3.03+dfsg1-4'),
    ('cowsay.full.swidtag', 'debian_7.4-x86_64-cowsay-3.03+dfsg1-4'),
    ('strongswan-tnc-imcvs.short.swidtag', 'fedora_19-x86_64-strongswan-tnc-imcvs-5.1.2-4.fc19'),
    ('strongswan-tnc-imcvs.full.swidtag', 'fedora_19-x86_64-strongswan-tnc-imcvs-5.1.2-4.fc19'),
])
def test_tag_unique_id(swidtag, filename, unique_id):
    assert swidtag.unique_id == unique_id


@pytest.mark.parametrize(['filename', 'version_str'], [
    ('strongswan.short.swidtag', '4.5.2-1.5+deb7u3'),
    ('strongswan.full.swidtag', '4.5.2-1.5+deb7u3'),
    ('cowsay.short.swidtag', '3.03+dfsg1-4'),
    ('cowsay.full.swidtag', '3.03+dfsg1-4'),
    ('strongswan-tnc-imcvs.short.swidtag', '5.1.2-4.fc19'),
    ('strongswan-tnc-imcvs.full.swidtag', '5.1.2-4.fc19'),
])
def test_tag_version(swidtag, filename, version_str):
    assert swidtag.version_str == version_str


@pytest.mark.parametrize(['filename', 'tagroles'], [
    ('strongswan.short.swidtag', [EntityRole.TAG_CREATOR]),
    ('strongswan.full.swidtag', [EntityRole.TAG_CREATOR, EntityRole.DISTRIBUTOR]),
    ('strongswan.full.swidtag.combinedrole',
     [EntityRole.TAG_CREATOR, EntityRole.DISTRIBUTOR, EntityRole.LICENSOR]),
    ('cowsay.short.swidtag', [EntityRole.TAG_CREATOR]),
    ('cowsay.full.swidtag', [EntityRole.TAG_CREATOR, EntityRole.LICENSOR]),
    ('strongswan-tnc-imcvs.short.swidtag', [EntityRole.TAG_CREATOR]),
    ('strongswan-tnc-imcvs.full.swidtag', [EntityRole.TAG_CREATOR]),
])
def test_tag_entity_roles(swidtag, filename, tagroles):
    roles = [i.role for i in swidtag.entityrole_set.all()]
    assert sorted(roles) == sorted(tagroles)


@pytest.mark.parametrize('filename', [
    'strongswan.short.swidtag',
    'strongswan.full.swidtag',
    'cowsay.short.swidtag',
    'cowsay.full.swidtag',
    'strongswan-tnc-imcvs.short.swidtag',
    'strongswan-tnc-imcvs.full.swidtag',
])
def test_tag_xml(swidtag, filename):
    with open('tests/test_tags/%s' % filename, 'r') as swid_file:
        swid_tag_xml = swid_file.read()
        swid_tag_xml_pretty = utils.prettify_xml(swid_tag_xml)
        assert swidtag.swid_xml == swid_tag_xml_pretty


@pytest.mark.parametrize(['filename', 'directories', 'files', 'filecount'], [
    ('strongswan.full.swidtag', ['/usr/share/doc/strongswan'], [
        'README.gz',
        'CREDITS.gz',
        'README.Debian.gz',
        'NEWS.Debian.gz',
        'changelog.gz',
    ], 7),
    ('cowsay.full.swidtag', ['/usr/share/cowsay/cows', '/usr/games'], [
        'cowsay',
        'cowthink',
        'vader-koala.cow',
        'elephant-in-snake.cow',
        'ghostbusters.cow',
    ], 61),
    ('strongswan-tnc-imcvs.full.swidtag', ['/usr/lib64/strongswan', '/usr/lib64/strongswan/imcvs'], [
        'libradius.so.0',
        'libtnccs.so.0.0.0',
        'imv-attestation.so',
        'imv-test.so',
    ], 35),
])
def test_tag_files(swidtag, filename, directories, files, filecount):
    assert File.objects.filter(name__in=files).count() == len(files)
    assert Directory.objects.filter(path__in=directories).count() == len(directories)
    assert swidtag.files.count() == filecount


@pytest.mark.django_db
@pytest.mark.parametrize('filename', [
    'strongswan.full.swidtag.notagcreator',
    'strongswan.full.swidtag.nouniqueid',
    'strongswan.full.swidtag.emptyuniqueid',
    'strongswan.full.swidtag.emptyregid'
])
def test_invalid_tags(filename):
    with open('tests/test_tags/invalid_tags/%s' % filename) as f:
        xml = f.read()
        # an invalid tag should raise an ValueError
        with pytest.raises(ValueError):
            tag, replaced = utils.process_swid_tag(xml)
        assert len(Tag.objects.all()) == 0
        assert len(Entity.objects.all()) == 0


@pytest.mark.parametrize('value', ['distributor', 'licensor', 'tagCreator'])
def test_valid_role(value):
    try:
        EntityRole.xml_attr_to_choice(value)
    except ValueError:
        pytest.fail('Role %s should be valid.' % value)


def test_invalid_role():
    with pytest.raises(ValueError):
        EntityRole.xml_attr_to_choice('licensee')


### TAG REPLACEMENT / UPDATE TESTS ###

@pytest.mark.parametrize('filename', [
    'strongswan.full.swidtag',
])
def test_tag_add_entities(swidtag, filename):
    assert swidtag.entityrole_set.count() == 2
    old_software_id = swidtag.software_id
    with open('tests/test_tags/strongswan.full.swidtag.replacement') as f:
        xml = f.read()
        tag, replaced = utils.process_swid_tag(xml, allow_tag_update=True)

    assert tag.software_id == old_software_id
    assert replaced is True
    assert tag.entity_set.count() == 4


@pytest.mark.parametrize('filename', [
    'strongswan.full.swidtag',
])
def test_tag_replace_files(swidtag, filename):
    assert swidtag.files.count() == 7

    with open('tests/test_tags/strongswan.full.swidtag.replacement') as f:
        xml = f.read()
        tag, replaced = utils.process_swid_tag(xml, allow_tag_update=True)

    assert replaced is True
    assert tag.files.count() == 3


@pytest.mark.parametrize('filename', [
    'invalid_tags/strongswan.full.swidtag.duplicateregid',
])
def test_change_duplicate_regid_entity_name(swidtag, filename):
    """
    Changing the name of an entity (with a role other than tagCreator) will create
    a new entity, since an entity is uniquely identified by its name and regid.

    """

    assert Entity.objects.count() == 1
    assert swidtag.entity_set.count() == 2
    new_xml = swidtag.swid_xml.replace('name="strongSwan"', 'name="strongswan123"')
    tag, replaced = utils.process_swid_tag(new_xml, allow_tag_update=True)
    assert tag.entity_set.count() == 2
    assert Entity.objects.count() == 1
    assert Tag.objects.count() == 1
    assert replaced is True

    # new entities should be wired up correctly
    test_entities = ['HSR', 'HSR']
    real_entities = tag.entity_set.values_list('name', flat=True)
    assert sorted(test_entities) == sorted(real_entities)


@pytest.mark.parametrize('filename', [
    'strongswan.full.swidtag',
])
def test_change_entity_name(swidtag, filename):
    entity_to_update = Entity.objects.get(regid='strongswan.org')
    old_entity_name = 'strongSwan'
    new_entity_name = 'strongSwan Project'

    assert Entity.objects.count() == 2
    assert swidtag.entity_set.count() == 2
    assert entity_to_update.name == old_entity_name

    new_xml = swidtag.swid_xml.replace('name="%s"' % old_entity_name, 'name="%s"' % new_entity_name)
    tag, replaced = utils.process_swid_tag(new_xml, allow_tag_update=False)
    entity_to_update = Entity.objects.get(regid='strongswan.org')

    assert Entity.objects.count() == 2
    assert tag.entity_set.count() == 2
    assert entity_to_update.name == new_entity_name


@pytest.mark.parametrize('filename', [
    'strongswan.full.swidtag',
])
def test_change_tagcreator_entity_regid(swidtag, filename):
    """
    Changing a tagCreator entity creates a new tag, since a tag is uniquely identified
    by the regid (of the tagCreator entity) and the unique_id of the tag itself.
    """
    new_xml = swidtag.swid_xml.replace('name="strongSwan" regid="strongswan.org"',
                                       'name="strongSwan" regid="strongswan.net"')
    tag, replaced = utils.process_swid_tag(new_xml, allow_tag_update=True)
    assert Tag.objects.count() == 2
    assert 'strongswan.net' in tag.software_id
    assert replaced is False


@pytest.mark.parametrize('filename', [
    'strongswan.full.swidtag',
])
def test_remove_distributor_entity(swidtag, filename):
    assert swidtag.entity_set.count() == 2
    with open('tests/test_tags/strongswan.full.swidtag.singleentity') as f:
        xml = f.read()
        tag, replaced = utils.process_swid_tag(xml, allow_tag_update=True)
        assert replaced is True
        assert tag.entity_set.count() == 1


@pytest.mark.parametrize('value', ['distributor', 'licensor', 'tagCreator'])
def test_valid_role(value):
    try:
        EntityRole.xml_attr_to_choice(value)
    except ValueError:
        pytest.fail('Role %s should be valid.' % value)


def test_invalid_role():
    with pytest.raises(ValueError):
        EntityRole.xml_attr_to_choice('licensee')


@pytest.fixture
def tags_and_sessions(transactional_db):
    now = timezone.now()
    s1 = baker.make(Session, id=1, identity__data="tester", time=now - timedelta(days=3), device__id=1)
    s2 = baker.make(Session, id=2, identity__data="tester", time=now - timedelta(days=1), device__id=1)
    s3 = baker.make(Session, id=3, identity__data="tester", time=now + timedelta(days=1), device__id=1)
    baker.make(Session, id=7, identity__data="tester", time=now + timedelta(days=2), device__id=1)
    s4 = baker.make(Session, id=4, identity__data="tester", time=now + timedelta(days=3), device__id=1)
    baker.make(Session, id=5, identity__data="tester", time=now - timedelta(days=4), device__id=1)
    baker.make(Session, id=6, identity__data="tester", time=now + timedelta(days=4), device__id=1)

    tag1 = baker.make(Tag, id=1, unique_id='tag1')
    tag2 = baker.make(Tag, id=2, unique_id='tag2')
    tag3 = baker.make(Tag, id=3, unique_id='tag3')
    tag4 = baker.make(Tag, id=4, unique_id='tag4')
    tag5 = baker.make(Tag, id=5, unique_id='tag5')
    tag6 = baker.make(Tag, id=6, unique_id='tag6')
    tag7 = baker.make(Tag, id=7, unique_id='tag7')

    # intital set: tag 1-4
    s1.tag_set.add(tag1, tag2, tag3, tag4)
    utils.update_tag_stats(s1, [1, 2, 3, 4])

    # s2, added: tag5;
    s2.tag_set.add(tag1, tag2, tag3, tag4, tag5)
    utils.update_tag_stats(s2, [1, 2, 3, 4, 5])

    # s3, removed: tag1;
    s3.tag_set.add(tag2, tag3, tag4, tag5)
    utils.update_tag_stats(s3, [2, 3, 4, 5])

    # s4 added: tag6, tag7; removed: tag2;
    s4.tag_set.add(tag3, tag4, tag5, tag6, tag7)
    utils.update_tag_stats(s4, [3, 4, 5, 6, 7])

    return {
        'now': now,
        'sessions': [s1, s2, s3, s4],
        'tags': [tag1, tag2, tag3, tag4, tag5, tag6, tag6]
    }


def test_swid_inventory_list_producer(transactional_db, tags_and_sessions):
    s1 = tags_and_sessions['sessions'][0]

    params = {'session_id': 1}
    tags = swid_inventory_list_producer(0, 10, None, params)
    assert len(tags) == 4
    assert tags[0]['first_seen'] == s1
    assert tags[0]['added_now'] is True

    params = {'session_id': 2}
    tags = swid_inventory_list_producer(0, 10, None, params)
    assert len(tags) == 5
    assert tags[0]['added_now'] is False

    params = {'session_id': 4}
    tags = swid_inventory_list_producer(0, 10, None, params)
    assert len(tags) == 5
    assert tags[0]['first_seen'] == s1

    params = {'session_id': 4}
    tags = swid_inventory_list_producer(0, 1, None, params)
    assert len(tags) == 1  # test paging

    params = {'session_id': 4}
    tags = swid_inventory_list_producer(0, 10, 'tag5', params)
    assert len(tags) == 1  # test filter
    assert tags[0]['tag'].unique_id == 'tag5'

    params = None
    tags = swid_inventory_list_producer(0, 10, 'tag5', params)
    assert len(tags) == 0
    assert tags == []


def test_swid_inventory_stat_producer(transactional_db, tags_and_sessions):
    params = {'session_id': 1}
    page_count = swid_inventory_stat_producer(1, None, params)
    assert page_count == 4

    page_count = swid_inventory_stat_producer(1, 'tag1', params)
    assert page_count == 1

    page_count = swid_inventory_stat_producer(2, None, params)
    assert page_count == 2

    page_count = swid_inventory_stat_producer(3, None, params)
    assert page_count == 2

    page_count = swid_inventory_stat_producer(4, None, params)
    assert page_count == 1

    page_count = swid_inventory_stat_producer(5, None, params)
    assert page_count == 1


def test_swid_log(transactional_db, tags_and_sessions):
    now = tags_and_sessions['now']

    from_timestamp = format(now - timedelta(days=3), 'U')
    to_timestamp = format(now + timedelta(days=4), 'U')

    params = {
        'device_id': 1,
        'from_timestamp': int(from_timestamp),
        'to_timestamp': int(to_timestamp),
    }
    data = swid_log_list_producer(0, 100, None, params)

    s1 = tags_and_sessions['sessions'][0]
    s2 = tags_and_sessions['sessions'][1]
    s3 = tags_and_sessions['sessions'][2]
    s4 = tags_and_sessions['sessions'][3]

    # there should be four results, bc. 4 session in the range have tags
    assert len(data) == 4

    assert len(data[s4]) == 3
    assert len(data[s3]) == 1
    assert len(data[s2]) == 1
    assert len(data[s1]) == 4
    # checking if removed and added are as expected
    assert data[s3][0].added is False
    assert data[s2][0].added is True

    # test omitted params
    data = swid_log_list_producer(0, 100, None, None)
    assert data == []

    # test filter query
    data = swid_log_list_producer(0, 100, 'tag1', params)
    assert len(data) == 2
    assert len(data[s1]) == 1
    assert len(data[s3]) == 1

    ## test single session selects:
    # test only last most recent session
    from_timestamp = format(now + timedelta(days=3), 'U')
    to_timestamp = format(now + timedelta(days=4), 'U')
    params = {
        'device_id': 1,
        'from_timestamp': int(from_timestamp),
        'to_timestamp': int(to_timestamp),
    }
    data = swid_log_list_producer(0, 100, None, params)
    assert len(data) == 1
    # only the added tags
    assert len(data[s4]) == 2

    # test only first session
    from_timestamp = format(now - timedelta(days=4), 'U')
    to_timestamp = format(now - timedelta(days=3), 'U')
    params = {
        'device_id': 1,
        'from_timestamp': int(from_timestamp),
        'to_timestamp': int(to_timestamp),
        }
    data = swid_log_list_producer(0, 100, None, params)
    assert len(data) == 1
    # only the added tags
    assert len(data[s1]) == 4


def test_get_installed_tags_with_time(transactional_db, tags_and_sessions):
    s1 = tags_and_sessions['sessions'][0]  # -3 days old
    s2 = tags_and_sessions['sessions'][1]  # -1 day old
    s3 = tags_and_sessions['sessions'][2]  # + 1 day
    s4 = tags_and_sessions['sessions'][3]  # + 3 days

    tag3 = tags_and_sessions['tags'][2]
    tag5 = tags_and_sessions['tags'][4]

    installed_tags = Tag.get_installed_tags_with_time(s4)
    # five tags installed in session s4
    assert len(installed_tags) == 5
    # tag3 was installed in session s1
    assert installed_tags.get(tag=tag3).first_seen == s1
    # tag5 was installed in session s2
    assert installed_tags.get(tag=tag5).first_seen == s2


@pytest.mark.parametrize('filename', [
    'strongswan.full.swidtag',
])
def test_changed_software_entity_name(swidtag, filename):
    new_xml = swidtag.swid_xml.replace('SoftwareIdentity name="strongswan"',
                                       'SoftwareIdentity name="strongswan123"')
    tag, replaced = utils.process_swid_tag(new_xml, allow_tag_update=True)
    assert replaced is True
    assert Tag.objects.count() == 1


def test_update_tag_stats(transactional_db):
    # Setup some sessions and tags
    now = timezone.now()
    s1 = baker.make(Session, id=1, identity__data="tester", time=now - timedelta(days=3), device__id=1)
    s2 = baker.make(Session, id=2, identity__data="tester", time=now - timedelta(days=2), device__id=1)
    s3 = baker.make(Session, id=3, identity__data="tester", time=now - timedelta(days=1), device__id=1)
    tags = [baker.make(Tag, id=n, unique_id='tag%i' % n) for n in range(10)]

    utils.update_tag_stats(s1, Tag.objects.values_list('pk', flat=True)[:4])

    # Last seen and first seen should be s1
    for tag_stat in TagStats.objects.all():
        assert tag_stat.last_seen == s1
        assert tag_stat.first_seen == s1

    with pytest.raises(TagStats.DoesNotExist):
        TagStats.objects.get(tag=tags[6], device=s1.device)

    utils.update_tag_stats(s2, Tag.objects.values_list('pk', flat=True)[2:4])

    # Only last_seen session for tags 2,3 should be changed
    assert TagStats.objects.get(tag=tags[0], device=s2.device).last_seen == s1
    assert TagStats.objects.get(tag=tags[0], device=s2.device).first_seen == s1
    assert TagStats.objects.get(tag=tags[1], device=s2.device).last_seen == s1
    assert TagStats.objects.get(tag=tags[1], device=s2.device).first_seen == s1

    assert TagStats.objects.get(tag=tags[2], device=s2.device).last_seen == s2
    assert TagStats.objects.get(tag=tags[2], device=s2.device).first_seen == s1
    assert TagStats.objects.get(tag=tags[3], device=s2.device).last_seen == s2
    assert TagStats.objects.get(tag=tags[3], device=s2.device).first_seen == s1


def test_large_tagstats_update(transactional_db):
    now = timezone.now()
    s1 = baker.make(Session, id=1, time=now, identity__data="tester")
    tags = [baker.make(Tag, id=n, unique_id='tag%i' % n) for n in range(2000)]
    tag_ids = range(2000)
    utils.update_tag_stats(s1, tag_ids)
    assert TagStats.objects.count() == 2000
