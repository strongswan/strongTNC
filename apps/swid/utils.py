# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import math

from django.db import transaction

from lxml import etree

from . import models
from apps.filesystem import models as filesystem_models


class SwidParser(object):
    """
    A SAX-like target parser for SWID XML files.
    """
    def __init__(self):
        self.tag = models.Tag()
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
            d, _ = filesystem_models.Directory.objects.get_or_create(path=dirname)
            f, _ = filesystem_models.File.objects.get_or_create(name=filename, directory=d)
            self.file_pks.append(f.pk)

    def close(self):
        """
        Fired when parsing is complete.
        """
        return self.tag, self.file_pks


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
    tag, file_pks = etree.fromstring(tag_xml.encode('utf8'), parser)
    # Parse and prettify the tag before saving
    tag.swid_xml = prettify_xml(tag_xml)
    tag.save()  # We need to save before we can add many-to-many relations

    # SQLite does not support >999 SQL parameters per query, so we need
    # to do manual chunking.
    block_size = 950
    block_count = int(math.ceil(len(file_pks) / block_size))
    tag.files = []  # Clear previously linked files first
    for i in xrange(block_count):
        TagFile = models.Tag.files.through  # The m2m intermediate model
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
