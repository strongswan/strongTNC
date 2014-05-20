# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals
"""
Custom manage.py command to create users and set their passwords.

Usage: ./manage.py setpassword [password]
"""

from getpass import getpass
from django.contrib.auth import get_user_model
from django.core.management.base import NoArgsCommand

from apps.auth.permissions import GlobalPermission


class Command(NoArgsCommand):
    """
    Required class to be recognized by manage.py.
    """
    help = 'Get or create admin-user and set password interactively'

    def handle_noargs(self, **kwargs):
        self.process_user('admin-user', write_access=True)
        self.process_user('readonly-user')
        self.stdout.write('Passwords updated succesfully!')

    def process_user(self, username, write_access=False):
        """
        Get or create user, set password and set permissions.

        Args:
            username (str):
                The desired username for the user.
            write_access (bool):
                Whether or not the user should get the `write_access`
                permission. Default ``False``.

        Returns: None

        """
        # Get or create user
        self.stdout.write('Looking for %s in database...' % username)
        User = get_user_model()
        user, new = User.objects.get_or_create(username=username)
        if new:
            self.stdout.write('--> User "%s" not found. Creating new user.' % username)

        # Set password
        pwd = getpass('--> Please enter a new password for %s: ' % username)
        user.set_password(pwd)
        user.save()

        # Set permissions
        if write_access:
            perm, _ = GlobalPermission.objects.get_or_create(codename='write_access')
            perm.name = 'Has write access to data.'
            perm.save()
            user.user_permissions.add(perm)
            self.stdout.write('--> Granting write_access permission.')
