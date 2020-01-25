import json
import os
import sys
from collections import namedtuple


# SETUP ######################################################################

# File locations
auth_loc = __file__
main_dir = os.path.abspath(os.path.join(auth_loc, '..'))
local_dir = os.path.abspath(os.path.join(main_dir, '..', 'local'))

# Globals
twitter = None
pgdb = None

# MAIN #######################################################################

# Objects
OauthCredentials = namedtuple('OauthCredentials',
    ['api_key', 'api_secret_key', 'access_token', 'access_token_secret'])

SqlCredentials = namedtuple('SqlCredentials',
    ['username', 'password'])

# Twitter
def _setup_twitter():
    global twitter
    twitter_fl = os.path.join(local_dir, 'twitter.json')
    with open(twitter_fl, 'r') as f:
        twitter_json = json.load(f)
    twitter = OauthCredentials(**twitter_json)


# Postgresql Database
def _setup_pgdb():
    global pgdb
    pgdb_fl = os.path.join(local_dir, 'pgdb.json')
    with open(pgdb_fl, 'r') as f:
        pgdb_json = json.load(f)
    pgdb = SqlCredentials(**pgdb_json)


_setup_twitter()
_setup_pgdb()

