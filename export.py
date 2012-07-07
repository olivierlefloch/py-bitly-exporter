#!/usr/bin/env python

# Requires https://github.com/bitly/bitly-api-python

import getopt
import sys
import urllib
import requests
import types

def main(argv=None):
    """
    This script exports all Bit.ly urls for an account.
    
    Required options:
        -l=, --login=: Bit.ly login
        -p=, --password=: Bit.ly Password (used to generate OAuth token)
    
    Optional parameters:
        -v: Verbose mode
        -h: Display this help and exit
        -u, --user: Export data for a user other than the login user
    """
    # Load options using getopt
    if argv is None:
        argv = sys.argv
    
    try:
        opts, args = getopt.getopt(
            argv[1:],
            "vhl:p:u:",
            ["help", "login=", "password=", "user="]
        )
    except getopt.error, msg:
        print "Option parsing error: %s" % str(msg)
        return 2
    
    # Setup defaults
    verbose = False
    login = None
    password = None
    user = None
    
    try:
        for option, value in opts:
            if option == "-v":
                verbose = True
            elif option in ("-h", "--help"):
                print main.__doc__
                return 0
            elif option in ("-l", "--login"):
                login = value
            elif option in ("-p", "--password"):
                password = value
            elif option in ("-u", "--user"):
                user = value
            else:
                raise Exception('unknown option')
    except Exception, err:
        print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err)
        print >> sys.stderr, "\t for help use --help"
        return 2
    
    if login is None:
        raise Exception('Login parameter must be present.')
    
    if password is None:
        raise Exception('Password parameter must be present.')
    
    bitly = Bitly(login, password, verbose)
    print bitly.user_link_history(user=user)

class Bitly(object):
    def __init__(self, login, password, verbose=False):
        super(Bitly, self).__init__()
        self.login = login
        self.verbose = verbose
        
        self.access_token = requests.post(
            'https://api-ssl.bitly.com/oauth/access_token',
            auth=(login, password),
            timeout=10
        )
        
        if verbose:
            print "Access token retrieved: %s" % self.access_token
        
    def user_link_history(self, limit=50, offset=0, user=None):
        params = {
            'limit': limit,
            'offset': offset,
            'archived': 'both'
        }
    
        if user is not None:
            params['user'] = user
    
        return self._call('v3/user/link_history', params)

    def _call(self, method, params):
        """
        A good chunk of the following method has been extracted from
        https://github.com/bitly/bitly-api-python
        """
        # default to json
        params['format'] = params.get('format','json')
        
        params['access_token'] = self.access_token
        
        # force to utf8 to fix ascii codec errors
        encoded_params = []
        for k,v in params.items():
            if type(v) in [types.ListType, types.TupleType]:
                v = [e.encode('UTF8') for e in v]
            else:
                v = str(v).encode('UTF8')
            encoded_params.append((k,v))
        params = dict(encoded_params)
        
        request = "https://api-ssl.bitly.com/%(method)s?%(params)s" % {
            'method': method,
            'params': urllib.urlencode(params, doseq=True)
        }
        
        http_response = requests.get(request, timeout=10)
        
        if http_response.status_code != 200:
            raise Exception('HTTP %d Error: %s' % (http_response.status_code, http_response.text))
        
        data = http_response.json
        
        if data is None or data.get('status_code', 500) != 200:
            raise Exception('Bitly returned error code %d: %s' % (data.get('status_code', 500), data.get('status_txt', 'UNKNOWN_ERROR')))
        
        return data

if __name__ == '__main__':
    sys.exit(main())
