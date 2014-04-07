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
A module to simulate a strongSwan IMV used for testing workitem generation
and session hannvoke by calling run_test()
"""

import httplib
import random
from datetime import datetime
from models import Session, Device, Identity

start_url = '/cmd/start_session'
end_url = '/cmd/end_session'


def start_login(params):
    """Call start url to invoke workItem generation."""

    con = httplib.HTTPConnection('localhost', 8000)
    url = '%s?%s' % (start_url, '&'.join(['%s=%s' % pair for pair in params.items()]))
    con.request('HEAD', url)
    response = con.getresponse()

    if response.status != 200:
        raise AssertionError('Expected: HTTP 200, got: HTTP %s' %
                response.status)

    body = response.read()
    if body != '':
        raise AssertionError('Expceted empty body, got: %s' % body)


def finish_login(params):
    """Call finish url to invoke result processing."""
    con = httplib.HTTPConnection('localhost', 8000)

    url = '%s?%s' % (end_url, '&'.join(['%s=%s' % pair for pair in params.items()]))
    con.request('HEAD', url)
    response = con.getresponse()

    if response.status != 200:
        raise AssertionError('Expected: HTTP 200, got: HTTP %s' %
                response.status)

    body = response.read()
    if body != '':
        raise AssertionError('Expceted empty body, got: %s' % body)


def run_test():
    """
    Run the test-case
    """
    device = Device.objects.get(value='deadbeef')
    identity = Identity.objects.get(data='tannerli')
    session = Session.objects.create(connectionID=random.randint(1, 65535),
                                     device=device, time=datetime.today(), identity=identity)

    params = {}
    params['sessionID'] = session.id

    start_login(params)

    # Simulate IMV, generate some random results
    for item in session.workitems.all():
        item.error = random.randint(0, 1)
        item.recommendation = random.choice((item.fail, item.noresult))
        item.result = ''
        item.save()

    finish_login(params)

    print 'OK'
