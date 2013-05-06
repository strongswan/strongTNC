import httplib,random
import models as m

start_url = '/cmd/start_session'
end_url  = '/cmd/end_session'

def start_login(params):
    """Call start url to invoke cygnet workItem generation."""

    con = httplib.HTTPConnection('localhost', 8000)
    url = '%s?%s' % (start_url, '&'.join(['%s=%s' % (k,v) for k,v in
        params.items()]))
    con.request('HEAD', url)
    response = con.getresponse()
    
    if response.status != 200:
        raise AssertionError('Expected: HTTP 200, got: HTTP %s' %
                response.status)

    body = response.read()
    if body != '':
        raise AssertionError('Expceted empty body, got: %s' % body)


def finish_login(params):
    """Call finish url to invoke cygnet result processing."""
    con = httplib.HTTPConnection('localhost', 8000)

    url = '%s?%s' % (end_url, '&'.join(['%s=%s' % (k,v) for k,v in
        params.items()]))
    con.request('HEAD', url)
    response = con.getresponse()
    
    if response.status != 200:
        raise AssertionError('Expected: HTTP 200, got: HTTP %s' %
                response.status)

    body = response.read()
    if body != '':
        raise AssertionError('Expceted empty body, got: %s' % body)

def run_test():
        params = dict()
        params['connectionID'] = 314159
        params['deviceID'] = 'deadbeef'
        params['osVersion'] = 'Ubuntu%2012.04'
        params['arID'] = 'tannerli'

        start_login(params)

        #Simulate IMV, generate some random results
        device = m.Device.objects.get(value=params['deviceID'])
        session = m.Session.objects.get(connectionID=params['connectionID'],
                device=device)
        
        for item in session.workitems.all():
            item.error = random.randint(0,1)
            item.recommendation = random.choice((item.fail, item.noresult))
            item.result = ''
            item.save()

        finish_login(params)

        session.delete()
        print 'OK'

