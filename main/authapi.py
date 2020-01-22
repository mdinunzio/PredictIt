import json
import os
import sys


auth_loc = __file__
main_dir = os.path.abspath(os.path.join(auth_loc, '..'))
local_dir = os.path.abspath(os.path.join(main_dir, '..', 'local'))

twitter_fl = os.path.join(local_dir, 'twitter.json')

with open(twitter_fl, 'r') as f:
    twitter = json.load(f)