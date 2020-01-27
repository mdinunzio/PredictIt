import pandas as pd
import urllib3
import json
import datetime
import os
import tweepy
import authapi
import predictit


# SETUP ######################################################################

# Pandas
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

# URLs and directories
USR_DIR = os.environ['USERPROFILE']
DESKTOP = os.path.join(USR_DIR, 'Desktop')

# Twitter
auth = tweepy.OAuthHandler(authapi.twitter.api_key,
                           authapi.twitter.api_secret_key)
auth.set_access_token(authapi.twitter.access_token,
                      authapi.twitter.access_token_secret)
twitter_api = tweepy.API(auth)


# MAIN #######################################################################

def get_tweet_counts(twitter_users=None):
    """
    Return a DataFrame of tweet counts for a given list of users.
    """
    if twitter_users is None:
        twitter_users = predictit.get_twitter_users()
    tweet_count_list = []
    for user in twitter_users:
        try:
            api_user = twitter_api.get_user(user)
            tweet_count = api_user.statuses_count
            d = {'user': user,
                 'tweets' : tweet_count}
            tweet_count_list.append(d)
        except Exception as e:
            print(e)
    tweet_counts = pd.DataFrame(tweet_count_list)
    return tweet_counts
