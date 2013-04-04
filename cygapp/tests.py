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

    def test_getGroupSet(self):
        device = m.Device(value='def', description='Test Device')
        device.save()
        
        g1 = m.Group(name='ROOT')
        g1.save()
        g11 = m.Group(name='B1.1', parent=g1)
        g11.save()
        g12 = m.Group(name='L1.2', parent=g1)
        g12.save()
        g13 = m.Group(name='B1.3', parent=g1)
        g13.save()
        g111 = m.Group(name='B1.1.1', parent=g11)
        g111.save()
        g1111 = m.Group(name='L1.1.1.1', parent=g111)
        g1111.save()
        g1112 = m.Group(name='L1.1.1.2', parent=g111)
        g1112.save()
        g131 = m.Group(name='L1.3.1', parent=g13)
        g131.save()
        g132 = m.Group(name='L1.3.2', parent=g13)
        g132.save()

        device.groups.add(g1112)
        device.groups.add(g131)
        device.save()

        groups = device.getGroupSet()
        self.assertEqual(6, len(groups))

        device.groups.add(g111)
        device.groups.add(g132)
        
        groups = device.getGroupSet()
        self.assertEqual(7, len(groups))

        print '\n'.join('%s' % g for g in groups)
        

        
    def test_imv_login(self):
        import simIMV as imv

        imv.run_test_case()


