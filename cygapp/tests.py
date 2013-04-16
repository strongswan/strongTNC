"""
Unit tests for the django app cygnet are specified in this file

    run using 'python manage.py test cygapp'
"""

from django.test import TestCase
from cygapp.policies import *
from datetime import datetime
import cygapp.models as m
import cygapp.views as v


class cygappTest(TestCase):
    def setUp(self):
        p = m.Product.objects.create(name='Fancy OS 3.14')
        device = m.Device.objects.create(value='def', description='Test Device', product=p)
        
        g1 = m.Group.objects.create(name='ROOT')
        g11 = m.Group.objects.create(name='B1.1', parent=g1)
        m.Group.objects.create(name='L1.2', parent=g1)
        g13 = m.Group.objects.create(name='B1.3', parent=g1)
        g111 = m.Group.objects.create(name='B1.1.1', parent=g11)
        m.Group.objects.create(name='L1.1.1.1', parent=g111)
        g1112 = m.Group.objects.create(name='L1.1.1.2', parent=g111)
        g131 = m.Group.objects.create(name='L1.3.1', parent=g13)
        m.Group.objects.create(name='L1.3.2', parent=g13)

        device.groups.add(g1112)
        device.groups.add(g131)
        device.save()

        m.Policy.objects.create(name='bash',type=1,argument='/bin/bash',fail=3,noresult=0)
        m.Policy.objects.create(name='usrbin',type=2,argument='/usr/bin/',fail=4,noresult=1)
        m.Policy.objects.create(name='ports',type=3,argument='0-1024',fail=0,noresult=0)

        lib = m.Package.objects.create(name='libstrongswan')
        ss = m.Package.objects.create(name='strongswan')
        ss_nm = m.Package.objects.create(name='strongswan-nm')
        ss_dbg = m.Package.objects.create(name='strongswan-dbg')
        ss_ike = m.Package.objects.create(name='strongswan-ikev1')

        m.Version.objects.create(time=datetime.today(), product=p, package=lib, release='1.1')
        m.Version.objects.create(time=datetime.today(), product=p, package=ss, release='0.9')
        m.Version.objects.create(time=datetime.today(), product=p, package=ss_nm, release='3.1')
        m.Version.objects.create(time=datetime.today(), product=p, package=ss_dbg, release='2.3')
        m.Version.objects.create(time=datetime.today(), product=p, package=ss_ike, release='1.1')

    def test_file_basics(self):
        """
        Tests basic file properties in different formats.
        """
        d = m.Directory.objects.create(path='/')
        f = m.File.objects.create(name='grep', directory=d)

        self.assertEqual('{"id": 1, "dir": "/", "name": "grep"}', f.__json__())

    def test_getGroupSet(self):
        device = m.Device.objects.get(value='def')

        groups = device.getGroupSet()
        self.assertEqual(6, len(groups))

        device.groups.add(m.Group.objects.get(name='B1.1.1'))
        device.groups.add(m.Group.objects.get(name='L1.3.2'))
        
        groups = device.getGroupSet()
        self.assertEqual(7, len(groups))

    def test_createWorkItems(self):

        g = m.Group.objects.get(name='B1.1.1')
        p = m.Policy.objects.get(name='bash')
        m.Enforcement.objects.create(group=g, policy=p, max_age=3)

        g = m.Group.objects.get(name='L1.3.1')
        p = m.Policy.objects.get(name='usrbin')
        m.Enforcement.objects.create(group=g, policy=p, max_age=2)

        user = m.Identity()
        user.type = 1
        user.data = 'foobar'
        user.save()
        
        device = m.Device.objects.get(value='def')

        measurement = m.Measurement()
        measurement.device = device
        measurement.time = datetime.today()
        measurement.connectionID = 123
        measurement.user = user
        measurement.save()

        device.createWorkItems(measurement)

        items = m.WorkItem.objects.filter(measurement=measurement)
        self.assertEqual(2, len(items))

        item = items[0]
        self.assertEqual(2, item.type)
        self.assertEqual(4, item.fail)
        self.assertEqual(1, item.noresult)
        self.assertEqual('/usr/bin/', item.argument)
        self.assertEqual(None, item.recommendation)
        self.assertEqual(None, item.result)


        item = items[1]
        self.assertEqual(1, item.type)
        self.assertEqual(3, item.fail)
        self.assertEqual(0, item.noresult)
        self.assertEqual('/bin/bash', item.argument)
        self.assertEqual(None, item.recommendation)
        self.assertEqual(None, item.result)
        

    def test_actionInheritance(self):

        #bash : fail=3 noresult=0
        g = m.Group.objects.get(name='B1.1.1')
        p = m.Policy.objects.get(name='bash')
        e1 = m.Enforcement(group=g, policy=p, max_age=3)
        e1.fail = None
        e1.noresult = None
        e1.save()

        e1 = m.Enforcement.objects.get(group=g, policy=p)

        #usrbin: fail=4 noresult=1
        g = m.Group.objects.get(name='L1.3.1')
        p = m.Policy.objects.get(name='usrbin')
        e2 = m.Enforcement(group=g, policy=p, max_age=2)
        e2.fail = 3
        e2.noresult = 0
        e2.save()

        user = m.Identity.objects.create(type=1, data='foobar')
        
        device = m.Device.objects.get(value='def')

        measurement = m.Measurement.objects.create(device=device,
                time=datetime.today(), connectionID=123, user=user)

        device.createWorkItems(measurement)

        item = m.WorkItem.objects.get(measurement=measurement, enforcement=e1)
        self.assertEqual(3, item.fail)
        self.assertEqual(0, item.noresult)

        
        item = m.WorkItem.objects.get(measurement=measurement, enforcement=e2)
        self.assertEqual(3, item.fail)
        self.assertEqual(0, item.noresult)


    def test_isDueFor(self):
        pass

    def test_generate_results(self):

        g = m.Group.objects.get(name='B1.1.1')
        p1 = m.Policy.objects.get(name='bash')
        e1 = m.Enforcement.objects.create(group=g, policy=p1, max_age=3)

        g = m.Group.objects.get(name='L1.3.1')
        p2 = m.Policy.objects.get(name='usrbin')
        e2 = m.Enforcement.objects.create(group=g, policy=p2, max_age=2)

        device = m.Device.objects.get(value='def')
        user = m.Identity.objects.create(type=1, data='foobar')
        measurement = m.Measurement.objects.create(device=device,
                time=datetime.today(), connectionID=123, user=user)
        
        m.WorkItem.objects.create(measurement=measurement, argument='asdf',
                fail=3, noresult=0, result='OK', recommendation=0, enforcement=e1,
                type=1)
        m.WorkItem.objects.create(measurement=measurement, argument='blubber',
                fail=3, noresult=0, result='FAIL', recommendation=3, enforcement=e2,
                type=2)

        v.generate_results(measurement)

        result = m.Result.objects.get(measurement=measurement, policy=p1)
        self.assertEqual('OK', result.result)
        self.assertEqual(0, result.recommendation)

        result = m.Result.objects.get(measurement=measurement, policy=p2)
        self.assertEqual('FAIL', result.result)
        self.assertEqual(3, result.recommendation)

        #TODO: According to tannerli/cygnet-doc#34, add testcases

    def test_imv_login(self):
        #This is no longer a simple test unit and dealt with in simIMV.py run
        # simIMV.run_test() to execute the test
        pass

