# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.db import transaction

from lxml import etree

from . import models
from tncapp import models as tncapp_models


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
            d, _ = tncapp_models.Directory.objects.get_or_create(path=dirname)
            f, _ = tncapp_models.File.objects.get_or_create(name=filename, directory=d)
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
    tag, file_pks = etree.fromstring(tag_xml, parser)
    # Parse and prettify the tag before saving
    tag.swid_xml = prettify_xml(tag_xml)
    tag.save()  # We need to save before we can add many-to-many relations
    tag.files = file_pks
    tag.save()

    return tag


def prettify_xml(xml, xml_declaration=True, encoding='UTF-8'):
    """
    Create a correctly indented (pretty) XML string from a parsable XML input.

    Args:
        xml (unicode):
            The XML string to be prettified
        xml_declaration (bool):
            Wheter a XML declaration should be added or not.
            Recommended for standalone documents.
        encoding (str):
            Value for the encoding attribute in the XML declaration.

    Returns:
        A prettified version of the given XML string.

    """
    xml_bytes = xml.encode(encoding)
    return etree.tostring(etree.fromstring(xml_bytes),
                          pretty_print=True,
                          xml_declaration=xml_declaration,
                          encoding=encoding,)