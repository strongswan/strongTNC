"""
Unit tests for the django app cygnet are specified in this file

    run using 'python manage.py test'
"""

from django.test import TestCase
from models import File, FileHash

class CygappTest(TestCase):
    def test_file_basics(self):
        """
        Tests basic file properties in different formats.
        """
        f = File()
        f.path="grep"
        f.type=0
        f.id=1
        f.save()

        h = File.objects.get(pk=1)
        self.assertEqual(0, h.type)
        self.assertEqual('{"path": "grep", "type": 0, "id": 1}', h.__json__())


