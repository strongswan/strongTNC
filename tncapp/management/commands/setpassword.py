"""
Custom manage.py command to set the admin user password

Usage: python manage.py setpassword [PASSWORD]
"""

from getpass import getpass
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    """
    Required class to be recognized by manage.py
    """

    help = 'Get or create admin-user and set password interactively'
    args = '[password]'

    def handle(self, *args, **kwargs):
        if len(args) > 1: raise CommandError('Too many arguments')

        self.stdout.write('looking for admin-user in database...')

        user, new = User.objects.get_or_create(username='admin-user')

        if new:
            self.stdout.write('... not found: creating new.')

        pwd = ''
        if len(args) > 0:
            pwd = args[0]

        if pwd == '':
            try:
                pwd = getpass('\nplease enter a new password for admin-user: ')
            except KeyboardInterrupt:
                self.stdout.write('\nabort')
                return

        user.set_password(pwd)
        user.save()

        self.stdout.write('password updated succesfully')
