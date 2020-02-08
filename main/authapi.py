import json
import os
import sys
import getpass
from dataclasses import dataclass


# SETUP ######################################################################

# File locations
auth_loc = __file__
main_dir = os.path.abspath(os.path.join(auth_loc, '..'))
local_dir = os.path.abspath(os.path.join(main_dir, '..', 'local'))

# Globals
twitter = None
pgdb = None
predictit = None


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


@dataclass
class PredictItCredentials:
    email: str
    password: str = ''


# Twitter
def _setup_twitter():
    """
    Set up the twitter OauthCredentials global variable.
    """
    global twitter
    twitter_fl = os.path.join(local_dir, 'twitter.json')
    with open(twitter_fl, 'r') as f:
        twitter_json = json.load(f)
    twitter = OauthCredentials(**twitter_json)


# Postgresql Database
def _setup_pgdb():
    """
    Set up the pgdb SqlCredentials global variable.
    """
    global pgdb
    pgdb_fl = os.path.join(local_dir, 'pgdb.json')
    with open(pgdb_fl, 'r') as f:
        pgdb_json = json.load(f)
    pgdb = SqlCredentials(**pgdb_json)


# PredictIt Cookies and header authorization
def _setup_predictit():
    """
    Set up the PredictItCredentials global variable.
    """
    global predictit
    predictit_fl = os.path.join(local_dir, 'predictit.json')
    with open(predictit_fl, 'r') as f:
        predictit_json = json.load(f)
    predictit = PredictItCredentials(**predictit_json)
    if predictit.password == '':
        pw = getpass.getpass('PredictIt Password: ')
        predictit.password = pw


_setup_twitter()
_setup_pgdb()
_setup_predictit()

