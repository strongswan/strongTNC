# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import math

from django.db import transaction

from lxml import etree

from apps.filesystem.models import Directory, File
from apps.swid.models import Entity, EntityRole
from .models import Tag


class SwidParser(object):
    """
    A SAX-like target parser for SWID XML files.
    """

    def __init__(self):
        self.tag = Tag()
        self.entities = []
        self.file_pks = []

    def start(self, tag, attrib):
        """
        Fired on element open. The data and children of the element are not yet
        available.
        """
        clean_tag = tag.split('}')[-1]  # Strip XSD part from tag name
        if clean_tag == 'SoftwareIdentity':
            # Store basic attributes
            self.tag.package_name = attrib['name']
            self.tag.unique_id = attrib['uniqueId']
            self.tag.version = attrib['version']
        elif clean_tag == 'File':
            # Store directories and files
            dirname = attrib['location']
            filename = attrib['name']
            d, _ = Directory.objects.get_or_create(path=dirname)
            f, _ = File.objects.get_or_create(name=filename, directory=d)
            self.file_pks.append(f.pk)
        elif clean_tag == 'Entity':
            # Store entities
            regid = attrib['regid']
            name = attrib['name']
            role = attrib['role']
            entity_role = EntityRole()
            entity, _ = Entity.objects.get_or_create(regid=regid, name=name)
            role = EntityRole.xml_attr_to_choice(role)

            entity_role.role = role
            self.entities.append((entity, entity_role))

            # Use regid of first entity with tagcreator role to construct software-id
            if role == EntityRole.TAGCREATOR:
                self.tag.software_id = '%s_%s' % (regid, self.tag.unique_id)

    def close(self):
        """
        Fired when parsing is complete.
        """
        return self.tag, self.file_pks, self.entities


@transaction.atomic
def process_swid_tag(tag_xml):
    """
    Parse a SWID XML tag and store the contained elements in the database.

    The tag must be a unicode object in order to be processed correctly.

    All database changes run in a transaction. When an error occurs, the
    database remains unchanged.

    Args:
       tag_xml (unicode):
           The SWID tag as an XML string.

    Returns:
       The newly created Tag model instance.

    """
    # Instantiate parser
    parser_target = SwidParser()
    parser = etree.XMLParser(target=parser_target, ns_clean=True)

    # Parse XML, save tag into database
    tag, file_pks, entities = etree.fromstring(tag_xml.encode('utf8'), parser)
    # Parse and prettify the tag before saving
    tag.swid_xml = prettify_xml(tag_xml)
    tag.save()  # We need to save before we can add many-to-many relations

    for entity, entity_role in entities:
        entity.save()

        # Wireup EntityRole object
        entity_role.tag = tag
        entity_role.entity = entity
        entity_role.save()

    # SQLite does not support >999 SQL parameters per query, so we need
    # to do manual chunking.
    block_size = 950
    block_count = int(math.ceil(len(file_pks) / block_size))
    tag.files = []  # Clear previously linked files first
    for i in xrange(block_count):
        TagFile = Tag.files.through  # The m2m intermediate model
        TagFile.objects.bulk_create([  # Create all the intermediate objects in a single query
                                       TagFile(tag_id=tag.pk, file_id=j)
                                       for j in file_pks[i * block_size:(i + 1) * block_size]
        ])

    return tag


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
    xml_bytes = xml.encode('utf8')
    return etree.tostring(etree.fromstring(xml_bytes),
                          pretty_print=True,
                          xml_declaration=xml_declaration,
                          encoding='UTF-8')
