#!/usr/bin/env python

# Requires https://github.com/bitly/bitly-api-python

import getopt
import sys
from bitly_api import bitly_api

# Monkey patch bitly_api to add user_link_history method
def __user_link_history(self, limit=50, offset=0, user=None):
    params = {
        'login': self.login,
        'apiKey': self.api_key,
        'limit': limit,
        'offset': offset,
        'archived': 'both'
    }
    
    if user is not None:
        params['user'] = user
    
    return self._call(self.host, 'v3/user/link_history', params, self.secret)
    
bitly_api.Connection.user_link_history = __user_link_history

def main(argv=None):
    """
    This script exports all Bit.ly urls for an account.
    
    Required options:
        -l=, --login=: Bit.ly login
        -k, --api_key=: Bit.ly (legacy) API Key
    
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
            "vhl:k:u:",
            ["help", "login=", "api_key=", "user="]
        )
    except getopt.error, msg:
        print "Option parsing error: %s" % str(msg)
        return 2
    
    # Setup defaults
    verbose = False
    login = None
    api_key = None
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
            elif option in ("-k", "--api_key"):
                api_key = value
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
    
    if api_key is None:
        raise Exception('API Key parameter must be present.')
    
    bitly = bitly_api.Connection(login, api_key)
    print bitly.user_link_history(50, 0, user)

if __name__ == '__main__':
    sys.exit(main())
