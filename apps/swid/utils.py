# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone

from lxml import etree

from apps.filesystem.models import Directory, File, FileHash, Algorithm
from apps.devices.models import Product
from apps.packages.models import Package, Version
from apps.swid.models import Entity, EntityRole, TagStats
from .models import Tag

"""
Maximum of nested <Directory> levels
"""
MAX_LEVEL = 32

"""
Namespace of SHA1, SHA256, SHA384 and SHA512 hash algorithms
"""
SHA1 = '{http://www.w3.org/2000/09/xmldsig#sha1}hash'
SHA256 = '{http://www.w3.org/2001/04/xmlenc#sha256}hash'
SHA384 = '{http://www.w3.org/2001/04/xmldsig-more#sha384}hash'
SHA512 = '{http://www.w3.org/2001/04/xmlenc#sha512}hash'

"""
NISTIR 8060 (n8060) namespace
"""
MUTABLE = '{http://csrc.nist.gov/schema/swid/2015-extensions/swid-2015-extensions-1.0.xsd}mutable'


class SwidParser(object):
    """
    A SAX-like target parser for SWID XML files.
    """

    def __init__(self):
        self.tag = Tag()
        self.entities = []
        self.files = []
        self.package = None
        self.version = None
        self.level = 0
        self.dir = ["" for x in range(MAX_LEVEL)]

    def start(self, tag, attrib):
        """
        Fired on element open. The data and children of the element are not yet
        available.
        """
        clean_tag = tag.split('}')[-1]  # Strip XSD part from tag name
        if clean_tag == 'SoftwareIdentity':
            # Store basic attributes
            self.tag.package_name = attrib['name']
            self.package, _ = Package.objects.get_or_create(name=self.tag.package_name)
            self.tag.version_str = attrib['version']
            if 'tagId' in attrib:
                self.tag.unique_id = attrib['tagId']
            else:
                # Fallback to SWID draft standard
                self.tag.unique_id = attrib['uniqueId']
        elif clean_tag == 'Meta':
            if 'product' in attrib:
                product = attrib['product']
                p, _ = Product.objects.get_or_create(name=product)
                self.version, _ = Version.objects.get_or_create(product=p,
                                    package=self.package, release=self.tag.version_str)
                # Update time
                self.version.time = timezone.now()
                self.version.save()
                self.tag.version = self.version
        elif clean_tag == 'Directory':
            # Increment <Directory> level
            self.level += 1
            if (self.level == MAX_LEVEL):
                raise ValueError("Maximum of %d nested <Directory> levels reached" % MAX_LEVEL)
            self.dir[self.level] = self.dir[self.level - 1]

            if 'root' in attrib and attrib['root'] != '/':
                self.dir[self.level] = attrib['root']
            if 'name' in attrib:
                self.dir[self.level] += '/' + attrib['name']
        elif clean_tag == 'File':
            # Store directories and files
            dirname = self.dir[self.level]
            if dirname == "":
                # Fallback to SWID draft standard
                dirname = attrib['location']
            filename = attrib['name']
            d, _ = Directory.objects.get_or_create(path=dirname)
            f, _ = File.objects.get_or_create(name=filename, directory=d)
            self.files.append(f)

            size = None
            if 'size' in attrib:
                size = int(attrib['size'])

            mutable = False
            if MUTABLE in attrib:
                if attrib[MUTABLE] == 'true':
                    mutable = True

            if SHA1 in attrib:
                a, _ = Algorithm.objects.get_or_create(name='SHA1')
                h, _ = FileHash.objects.get_or_create(version=self.version,
                           file=f, size=size, mutable=mutable, algorithm=a,
                           hash=attrib[SHA1].lower())
            if SHA256 in attrib:
                a, _ = Algorithm.objects.get_or_create(name='SHA256')
                h, _ = FileHash.objects.get_or_create(version=self.version,
                           file=f, size=size, mutable=mutable, algorithm=a,
                           hash=attrib[SHA256].lower())
            if SHA384 in attrib:
                a, _ = Algorithm.objects.get_or_create(name='SHA384')
                h, _ = FileHash.objects.get_or_create(version=self.version,
                           file=f, size=size, mutable=mutable, algorithm=a,
                           hash=attrib[SHA384].lower())
            if SHA512 in attrib:
                a, _ = Algorithm.objects.get_or_create(name='SHA512')
                h, _ = FileHash.objects.get_or_create(version=self.version,
                           file=f, size=size, mutable=mutable, algorithm=a,
                           hash=attrib[SHA512].lower())

        elif clean_tag == 'Entity':
            # Store entities
            regid = attrib['regid']
            name = attrib['name']
            roles = attrib['role']
            for role in roles.split():
                entity, _ = Entity.objects.get_or_create(regid=regid)
                entity.name = name

                role_id = EntityRole.xml_attr_to_choice(role)
                entity_role = EntityRole()
                entity_role.role = role_id
                self.entities.append((entity, entity_role))

                # Use regid of last entity with tagCreator role to construct software-id
                if role_id == EntityRole.TAG_CREATOR:
                    self.tag.software_id = '%s__%s' % (regid, self.tag.unique_id)

    def end(self, tag):
        clean_tag = tag.split('}')[-1]  # Strip XSD part from tag name
        if clean_tag == 'Directory':
            self.level -= 1

    def close(self):
        """
        Fired when parsing is complete.
        """
        if not self.tag.software_id:
            msg = 'A SWID tag (%s) without a `tagCreator` entity is currently not supported.'
            raise ValueError(msg % self.tag.unique_id)
        return self.tag, self.files, self.entities


@transaction.atomic
def process_swid_tag(tag_xml, allow_tag_update=False):
    """
    Parse a SWID XML tag and store the contained elements in the database.

    The tag must be a unicode object in order to be processed correctly.

    All database changes run in a transaction. When an error occurs, the
    database remains unchanged.

    Args:
       tag_xml (unicode):
           The SWID tag as an XML string.
       allow_tag_update (bool):
            If the tag already exists its data gets overwritten.

    Returns:
       A tuple containing the newly created Tag model instance and a flag
       whether a pre-existing tag was replaced or not.

    """
    # Instantiate parser
    parser_target = SwidParser()
    parser = etree.XMLParser(target=parser_target, ns_clean=True)

    # Parse XML, save tag into database
    try:
        tag, files, entities = etree.fromstring(tag_xml.encode('utf-8'), parser)
    except KeyError as ke:
        raise ValueError('Invalid tag: missing %s property' % ke.message)

    tag.swid_xml = prettify_xml(tag_xml)

    # Check whether tag already exists
    try:
        old_tag = Tag.objects.get(software_id=tag.software_id)
    # Tag doesn't exist, create a new one later on
    except Tag.DoesNotExist:
        replaced = False
    # Tag exists already
    else:
        # Tag already exists but updates are not allowed
        if not allow_tag_update:
            replaced = False
            # The tag will not be changed, but we want to make sure
            # that the entities have the right name.
            for entity, _ in entities:
                Entity.objects.filter(pk=entity.pk).update(name=entity.name)

            # Tag needs to be reloaded after entity updates
            return Tag.objects.get(pk=old_tag.pk), replaced
        # Update tag with new information
        old_tag.package_name = tag.package_name
        old_tag.version_str = tag.version_str
        old_tag.version = tag.version
        old_tag.unique_id = tag.unique_id
        old_tag.files.clear()
        chunked_bulk_add(old_tag.files, files, 980)
        old_tag.swid_xml = tag.swid_xml
        tag = old_tag
        tag.entity_set.clear()
        replaced = True

    # Validate and save tag and entity
    try:
        tag.full_clean()
        tag.save()  # We need to save before we can add many-to-many relations

        # Add entities
        for entity, entity_role in entities:
            entity.full_clean()
            entity.save()
            entity_role.tag = tag
            entity_role.entity = entity
            entity_role.full_clean()
            entity_role.save()
    except ValidationError as e:
        msgs = []
        for field, errors in e.error_dict.items():
            error_str = ' '.join([m for err in errors for m in err.messages])
            msgs.append('%s: %s' % (field, error_str))
        raise ValueError(' '.join(msgs))

    # SQLite does not support >999 SQL parameters per query, so we need
    # to do manual chunking.
    chunked_bulk_add(tag.files, files, 980)

    return tag, replaced


def prettify_xml(xml, xml_declaration=True):
    """
    Create a correctly indented (pretty) XML string from a parsable XML input.

    Args:
        xml (unicode):
            The XML string to be prettified
        xml_declaration (bool):
            Wheter a XML declaration should be added or not.
            Recommended for standalone documents.

    Returns:
        A prettified version of the given XML string.

    """
    xml_bytes = xml.encode('utf-8')
    return etree.tostring(etree.fromstring(xml_bytes),
                          pretty_print=True,
                          xml_declaration=xml_declaration,
                          encoding='UTF-8').decode('utf-8')


def chunked_bulk_add(manager, objects, block_size):
    """
    Add items to a reverse FK relation in chunks.

    Args:
        manager:
            The target model manager.
        objects:
            The objects to add to the target model.
        block_size:
            Number of objects per block.

    """
    for i in range(0, len(objects), block_size):
        pk_slice = objects[i:i + block_size]
        manager.add(*pk_slice)


def chunked_filter_in(queryset, filter_field, filter_list, block_size):
    """
    Select items from an ``field__in=filter_list`` filtered queryset in
    multiple queries.

    Example: If you have the following query ::

        SELECT * FROM items WHERE id IN (1, 2, 3, 4, 5, 6);

    ...and you want to do a chunked filtering with block size 2, the result is
    that the following queries are executed::

        SELECT * FROM items WHERE id IN (1, 2);
        SELECT * FROM items WHERE id IN (3, 4);
        SELECT * FROM items WHERE id IN (5, 6);

    Args:
        queryset:
            The base queryset.
        filter_field:
            The field to filter on.
        filter_list:
            The list of values for the ``IN`` filtering. This is the list that
            will be chunked.
        block_size:
            The number of items to filter by per query.

    Returns:
        Return a list containing all the items from all the querysets.

    """
    out = []
    for i in range(0, len(filter_list), block_size):
        filter_slice = filter_list[i:i + block_size]
        kwargs = {filter_field + '__in': filter_slice}
        items = list(queryset.filter(**kwargs))
        out.extend(items)
    return out


def update_tag_stats(session, tag_ids):
    new_tags = []
    block_size = 980
    for i in range(0, len(tag_ids), block_size):
        tag_ids_slice = tag_ids[i:i + block_size]
        # TODO: Instead of filtering the device tags, a list of all tags for a
        # device could be created outside of the loop.
        existing_tags = TagStats.objects.filter(device__pk=session.device_id,
                                                tag__pk__in=tag_ids_slice)
        new_tags.extend(set(tag_ids_slice) - set(existing_tags.values_list('tag__pk', flat=True)))
        existing_tags.update(last_seen=session)

    # Chunked create is done by default for sqlite,
    # see https://docs.djangoproject.com/en/dev/ref/models/querysets/#bulk-create
    TagStats.objects.bulk_create([
        TagStats(tag_id=t, device=session.device, first_seen=session, last_seen=session)
        for t in new_tags]
    )
