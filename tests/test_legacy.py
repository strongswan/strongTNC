from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from tncapp.models import WorkItem, Session, Policy, Enforcement, Action, Identity, Result
from apps.devices.models import Device, Group, Product
from apps.packages.models import Package, Version
from apps.filesystem.models import File, Directory
from tncapp.views import generate_results, purge_dead_sessions
from tncapp.policy_views import check_range


class TncappTest(TestCase):
    def setUp(self):
        user = Identity.objects.create(data='Test User', type=1)
        user.save()

        p = Product.objects.create(name='Fancy OS 3.14')
        device = Device.objects.create(value='def', description='Test Device', product=p)

        g1 = Group.objects.create(name='ROOT')
        g11 = Group.objects.create(name='B1.1', parent=g1)
        Group.objects.create(name='L1.2', parent=g1)
        g13 = Group.objects.create(name='B1.3', parent=g1)
        g111 = Group.objects.create(name='B1.1.1', parent=g11)
        Group.objects.create(name='L1.1.1.1', parent=g111)
        g1112 = Group.objects.create(name='L1.1.1.2', parent=g111)
        g131 = Group.objects.create(name='L1.3.1', parent=g13)
        Group.objects.create(name='L1.3.2', parent=g13)

        device.groups.add(g1112)
        device.groups.add(g131)
        device.save()

        Policy.objects.create(name='bash', type=1, argument='/bin/bash', fail=3, noresult=0)
        Policy.objects.create(name='usrbin', type=2, argument='/usr/bin/', fail=4, noresult=1)
        Policy.objects.create(name='ports', type=3, argument='0-1024', fail=0, noresult=0)

        lib = Package.objects.create(name='libstrongswan')
        ss = Package.objects.create(name='strongswan')
        ss_nm = Package.objects.create(name='strongswan-nm')
        ss_dbg = Package.objects.create(name='strongswan-dbg')
        ss_ike = Package.objects.create(name='strongswan-ikev1')

        Version.objects.create(time=timezone.now(), product=p, package=lib, release='1.1')
        Version.objects.create(time=timezone.now(), product=p, package=ss, release='0.9')
        Version.objects.create(time=timezone.now(), product=p, package=ss_nm, release='3.1')
        Version.objects.create(time=timezone.now(), product=p, package=ss_dbg, release='2.3')
        Version.objects.create(time=timezone.now(), product=p, package=ss_ike, release='1.1')

        dir = Directory.objects.create(path='/bin')
        File.objects.create(name='bash', directory=dir)

    def test_getGroupSet(self):
        device = Device.objects.get(value='def')

        groups = device.get_group_set()
        self.assertEqual(6, len(groups))

        device.groups.add(Group.objects.get(name='B1.1.1'))
        device.groups.add(Group.objects.get(name='L1.3.2'))

        groups = device.get_group_set()
        self.assertEqual(7, len(groups))

    def test_create_work_items(self):
        user = Identity.objects.get(pk=1)

        g = Group.objects.get(name='B1.1.1')
        p = Policy.objects.get(name='bash')
        Enforcement.objects.create(group=g, policy=p, max_age=3)

        g = Group.objects.get(name='L1.3.1')
        p = Policy.objects.get(name='usrbin')
        Enforcement.objects.create(group=g, policy=p, max_age=2)

        device = Device.objects.get(value='def')

        session = Session.objects.create(device=device, time=timezone.now(),
                connection_id=123, identity=user)

        device.create_work_items(session)

        items = WorkItem.objects.filter(session=session)
        self.assertEqual(2, len(items))

        item = items[0]
        self.assertEqual(2, item.type)
        self.assertEqual(4, item.fail)
        self.assertEqual(1, item.noresult)
        self.assertEqual('/usr/bin/', item.arg_str)
        self.assertEqual(None, item.recommendation)
        self.assertEqual(None, item.result)

        item = items[1]
        self.assertEqual(1, item.type)
        self.assertEqual(3, item.fail)
        self.assertEqual(0, item.noresult)
        self.assertEqual('/bin/bash', item.arg_str)
        self.assertEqual(None, item.recommendation)
        self.assertEqual(None, item.result)

    def test_actionInheritance(self):

        #bash : fail=3 noresult=0
        g = Group.objects.get(name='B1.1.1')
        p = Policy.objects.get(name='bash')
        e1 = Enforcement(group=g, policy=p, max_age=3)
        e1.fail = None
        e1.noresult = None
        e1.save()

        e1 = Enforcement.objects.get(group=g, policy=p)

        #usrbin: fail=4 noresult=1
        g = Group.objects.get(name='L1.3.1')
        p = Policy.objects.get(name='usrbin')
        e2 = Enforcement(group=g, policy=p, max_age=2)
        e2.fail = 3
        e2.noresult = 0
        e2.save()

        user = Identity.objects.create(data='foobar', type=5)

        device = Device.objects.get(value='def')

        session = Session.objects.create(device=device,
                time=timezone.now(), connection_id=123, identity=user)

        device.create_work_items(session)

        item = WorkItem.objects.get(session=session, enforcement=e1)
        self.assertEqual(3, item.fail)
        self.assertEqual(0, item.noresult)

        item = WorkItem.objects.get(session=session, enforcement=e2)
        self.assertEqual(3, item.fail)
        self.assertEqual(0, item.noresult)

    def test_is_due_for(self):
        g = Group.objects.get(name='L1.3.1')
        p = Policy.objects.get(name='usrbin')
        user = Identity.objects.create(data='foobar', type=5)
        device = Device.objects.get(value='def')
        e = Enforcement.objects.create(group=g, policy=p, max_age=2 * 86400)

        # No Session yet
        self.assertEqual(True, device.is_due_for(e))

        # Session yields no results for policy
        meas = Session.objects.create(device=device, time=timezone.now(),
                connection_id=123, identity=user)
        self.assertEqual(True, device.is_due_for(e))

        # Session is too old
        Result.objects.create(policy=p, session=meas, result='OK',
                recommendation=Action.ALLOW)

        meas.time -= timedelta(days=4)
        meas.save()
        self.assertEqual(True, device.is_due_for(e))

        meas.time = timezone.now() - timedelta(days=2, minutes=1)
        meas.save()
        self.assertEqual(True, device.is_due_for(e))

        meas.time = timezone.now() - timedelta(days=1, hours=23, minutes=59)
        meas.save()
        self.assertEqual(False, device.is_due_for(e))

    def test_generate_results(self):

        g = Group.objects.get(name='B1.1.1')
        p1 = Policy.objects.get(name='bash')
        e1 = Enforcement.objects.create(group=g, policy=p1, max_age=3)

        g = Group.objects.get(name='L1.3.1')
        p2 = Policy.objects.get(name='usrbin')
        e2 = Enforcement.objects.create(group=g, policy=p2, max_age=2)

        p3 = Policy.objects.get(name='ports')
        e3 = Enforcement.objects.create(group=g, policy=p3, max_age=4)

        device = Device.objects.get(value='def')
        user = Identity.objects.create(data='foobar', type=5)
        session = Session.objects.create(device=device,
                time=timezone.now(), connection_id=123, identity=user)

        WorkItem.objects.create(session=session, arg_str='asdf',
                fail=3, noresult=0, result='OK', recommendation=1, enforcement=e1,
                type=1)
        WorkItem.objects.create(session=session, arg_str='blubber',
                fail=3, noresult=0, result='FAIL', recommendation=3, enforcement=e2,
                type=2)
        WorkItem.objects.create(session=session, arg_str='sauce',
                fail=3, noresult=0, result='', enforcement=e3,
                type=2)

        generate_results(session)

        result = Result.objects.get(session=session, policy=p1)
        self.assertEqual('OK', result.result)
        self.assertEqual(1, result.recommendation)

        result = Result.objects.get(session=session, policy=p2)
        self.assertEqual('FAIL', result.result)
        self.assertEqual(3, result.recommendation)

        result = Result.objects.get(session=session, policy=p3)
        self.assertEqual('', result.result)
        self.assertEqual(3, result.recommendation)

    def test_imv_login(self):
        #This is no longer a simple test unit and dealt with in simIMV.py run
        # simIMV.run_test() to execute the test
        pass

    def test_policy_file_protection(self):
        file = File.objects.get(name='bash')

        policy = Policy.objects.create(name='binbash', type=1, argument='%d' % file.id,
                file=file, fail=Action.BLOCK, noresult=Action.ALLOW)

        from django.db.models.deletion import ProtectedError
        self.assertRaises(ProtectedError, file.delete)
        policy.delete()
        file.delete()

    def test_policy_dir_protection(self):
        dir = Directory.objects.get(path='/bin')

        policy = Policy.objects.create(name='binhashes', type=2,
                argument='%d' % dir.id, dir=dir, fail=Action.BLOCK,
                noresult=Action.ALLOW)

        from django.db.models.deletion import ProtectedError
        self.assertRaises(ProtectedError, dir.delete)
        policy.delete()
        dir.delete()

    def test_check_range(self):
        self.assertEqual(True, check_range('1'))
        self.assertEqual(True, check_range('65535'))
        self.assertEqual(True, check_range('0-65535'))
        self.assertEqual(True, check_range(''))
        self.assertEqual(True, check_range('4 5-100 8000'))
        self.assertEqual(True, check_range('4    5-100     8000'))
        self.assertEqual(True, check_range(' 4 5-100 8000'))
        self.assertEqual(True, check_range('4 5-100 8000    '))
        self.assertEqual(True, check_range('2  '))

        self.assertEqual(False, check_range('  11000 -  12123    5-10'))
        self.assertEqual(False, check_range('  11000 -  12123 ,    5-10'))
        self.assertEqual(False, check_range('11000-12123,5-10'))
        self.assertEqual(False, check_range('1-2,3-4,10000-20000'))
        self.assertEqual(False, check_range('1, 2, 3, 4, 5'))
        self.assertEqual(False, check_range('1,2,3,4,5'))
        self.assertEqual(False, check_range(','))
        self.assertEqual(False, check_range('-'))
        self.assertEqual(False, check_range(', ,'))
        self.assertEqual(False, check_range('1-'))
        self.assertEqual(False, check_range('1- '))
        self.assertEqual(False, check_range('10-5'))
        self.assertEqual(False, check_range('1,3,11-2'))
        self.assertEqual(False, check_range('1,2,a,4'))
        self.assertEqual(False, check_range('1-10, 25555-25000'))
        self.assertEqual(False, check_range('1-65536'))

    def test_purge_dead_sessions(self):
        device = Device.objects.get(pk=1)
        id = Identity.objects.create(data='user', type=5)

        time = timezone.now() - timedelta(days=20)
        Session.objects.create(device=device, identity=id, time=time, connection_id=1)

        time = timezone.now() - timedelta(days=7)
        Session.objects.create(device=device, identity=id, time=time, connection_id=2)

        time = timezone.now() - timedelta(days=3)
        Session.objects.create(device=device, identity=id, time=time, connection_id=3)

        time = timezone.now() - timedelta(days=10)
        Session.objects.create(device=device, identity=id, time=time, connection_id=4,
                recommendation=Action.BLOCK)

        time = timezone.now() - timedelta(days=10)
        Session.objects.create(device=device, identity=id, time=time, connection_id=5,
                recommendation=Action.ALLOW)

        purge_dead_sessions()
        sessions = Session.objects.all()

        self.assertEqual(3, len(sessions))
        for session in sessions:
            self.assertTrue(session.id in (3, 4, 5))
