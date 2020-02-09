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
pgdb_dev = None
pgdb_prod = None
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
    username: str
    password: str
    host: str
    port: int
    db: str


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
def _setup_pgdb_dev():
    """
    Set up the pgdb_dev SqlCredentials global variable.
    """
    global pgdb_dev
    pgdb_fl = os.path.join(local_dir, 'pgdb_dev.json')
    with open(pgdb_fl, 'r') as f:
        pgdb_json = json.load(f)
    pgdb_dev = SqlCredentials(**pgdb_json)


def _setup_pgdb_prod():
    """
    Set up the pgdb_prod SqlCredentials global variable.
    """
    global pgdb_prod
    pgdb_fl = os.path.join(local_dir, 'pgdb_prod.json')
    with open(pgdb_fl, 'r') as f:
        pgdb_json = json.load(f)
    pgdb_prod = SqlCredentials(**pgdb_json)


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


_setup_twitter()
_setup_pgdb_dev()
_setup_pgdb_prod()
_setup_predictit()

