import models as m
import random, httplib

start_url = '/cygapp/cmd/startlogin/'
end_url  = '/cygapp/cmd/finishlogin/'
deviceID = 'deadbeef'

def start_login():
    """Call start url to invoke cygnet workItem generation."""

    con = httplib.HTTPConnection('localhost', 8000)
    con.request('HEAD', start_url + deviceID)
    response = con.getresponse()
    
    if response.status != 200:
        raise AssertionError('Expected: HTTP 200, got: HTTP %s' %
                response.status)

    body = response.read()
    if body != '':
        raise AssertionError('Expceted empty body, got: %s' % body)


def finish_login():
    """Call finish url to invoke cygnet result processing."""
    con = httplib.HTTPConnection('localhost', 8000)
    con.request('HEAD', end_url + deviceID)
    response = con.getresponse()
    
    if response.status != 200:
        raise AssertionError('Expected: HTTP 200, got: HTTP %s' %
                response.status)

    body = response.read()
    if body != '':
        raise AssertionError('Expceted empty body, got: %s' % body)

def run_test_case():
    start_login()

    #Simulate IMV, generate some random results
    device = m.Device.objects.get(value=deviceID)

    if not device.workitems:
        raise ValueError('Received no workitems for %s' % device.id)

    for item in device.workitems:
        item.error = random.randint(0,1)
        item.recommendation = random.choice((item.fail, item.default))
        item.save()

    finish_login()

if __name__ != '__main__':
    run_test_case()
else: print 'Can only run as module'



