"""
Unit tests for the django app cygnet are specified in this file

    run using 'python manage.py test cygapp'
"""

from django.test import TestCase
from cygapp.policies import *
from datetime import datetime, timedelta
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

        dir = m.Directory.objects.create(path='/bin')
        m.File.objects.create(name='bash', directory=dir)

    def test_getGroupSet(self):
        device = m.Device.objects.get(value='def')

        groups = device.get_group_set()
        self.assertEqual(6, len(groups))

        device.groups.add(m.Group.objects.get(name='B1.1.1'))
        device.groups.add(m.Group.objects.get(name='L1.3.2'))
        
        groups = device.get_group_set()
        self.assertEqual(7, len(groups))

    def test_create_work_items(self):

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

        device.create_work_items(measurement)

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

        device.create_work_items(measurement)

        item = m.WorkItem.objects.get(measurement=measurement, enforcement=e1)
        self.assertEqual(3, item.fail)
        self.assertEqual(0, item.noresult)

        
        item = m.WorkItem.objects.get(measurement=measurement, enforcement=e2)
        self.assertEqual(3, item.fail)
        self.assertEqual(0, item.noresult)


    def test_is_due_for(self):
        g = m.Group.objects.get(name='L1.3.1')
        p = m.Policy.objects.get(name='usrbin')
        user = m.Identity.objects.create(type=1, data='foobar')
        device = m.Device.objects.get(value='def')
        e = m.Enforcement.objects.create(group=g, policy=p, max_age=2)

        #No Measurement yet
        self.assertEqual(True, device.is_due_for(e))

        #Measurement yields no results for policy
        meas = m.Measurement.objects.create(device=device, time=datetime.today(),
                connectionID=123, user=user)
        self.assertEqual(True, device.is_due_for(e))


        #Measurement is too old
        m.Result.objects.create(policy=p, measurement=meas, result='OK',
                recommendation = m.Action.ALLOW)

        meas.time -= timedelta(days=4)
        meas.save()
        self.assertEqual(True, device.is_due_for(e))

        meas.time = datetime.today() - timedelta(days=2, minutes=1)
        meas.save()
        self.assertEqual(True, device.is_due_for(e))

        meas.time = datetime.today() - timedelta(days=1, hours=23, minutes=59)
        meas.save()
        self.assertEqual(False, device.is_due_for(e))

        #TODO: Insert test cases for when last result wasn't OK, see
        #tannerli/cygnet-doc#35 for more info

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

    def test_policy_file_protection(self):
        file = m.File.objects.get(name='bash')

        policy = m.Policy.objects.create(name='binbash', type=1, argument='%d'%file.id,
                file=file, fail=m.Action.BLOCK, noresult=m.Action.ALLOW)

        from django.db.models.deletion import ProtectedError
        self.assertRaises(ProtectedError, file.delete)
        policy.delete()
        file.delete()

    def test_policy_dir_protection(self):
        dir = m.Directory.objects.get(path='/bin')

        policy = m.Policy.objects.create(name='binhashes', type=2,
                argument='%d'%dir.id, dir=dir, fail=m.Action.BLOCK,
                noresult=m.Action.ALLOW)

        from django.db.models.deletion import ProtectedError
        self.assertRaises(ProtectedError, dir.delete)
        policy.delete()
        dir.delete()

