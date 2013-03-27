"""
Unit tests for the django app cygnet are specified in this file

    run using 'python manage.py test cygapp'
"""

from django.test import TestCase
import cygapp.models as m

class CygappTest(TestCase):
    def test_file_basics(self):
        """
        Tests basic file properties in different formats.
        """
        f = m.File(name='grep')
        d = m.Directory(path='/')
        d.save()
        f.directory=d
        f.save()

        h = m.File.objects.get(pk=1)
        self.assertEqual('{"id": 1, "dir": "/", "name": "grep"}', h.__json__())

    def test_imv_login(self):
        import simIMV as imv

        imv.run_test_case()

