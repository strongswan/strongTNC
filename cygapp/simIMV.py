import  httplib

start_url = '/cmd/start_measurement'
end_url  = '/cmd/finish_measurement'

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

    url = '%s?connectionID=%s' % params['connectionID']
    con.request('HEAD', url)
    response = con.getresponse()
    
    if response.status != 200:
        raise AssertionError('Expected: HTTP 200, got: HTTP %s' %
                response.status)

    body = response.read()
    if body != '':
        raise AssertionError('Expceted empty body, got: %s' % body)

