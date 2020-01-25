import json
import os
import sys
from dataclasses import dataclass
from sympy.printing import str


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

@dataclass
class OauthCredentials:
    api_key: str
    api_secret_key: str
    access_token: str
    access_token_secret: str

@dataclass
class SqlCredentials:
    db_name: str
    username: str
    password: str

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

