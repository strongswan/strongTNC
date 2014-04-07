#
# Copyright (C) 2013 Marco Tanner
# HSR University of Applied Sciences Rapperswil
#
# This file is part of strongTNC.  strongTNC is free software: you can
# redistribute it and/or modify it under the terms of the GNU Affero General
# Public License as published by the Free Software Foundation, either version 3
# of the License, or (at your option) any later version.
#
# strongTNC is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License
# along with strongTNC.  If not, see <http://www.gnu.org/licenses/>.
#

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
        if len(args) > 1:
            raise CommandError('Too many arguments')

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
