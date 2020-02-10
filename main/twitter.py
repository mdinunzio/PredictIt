import pandas as pd
import urllib3
import json
import datetime
import os
import tweepy
import authapi
import predictit
import sqlalchemy


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
                 'tweets': tweet_count}
            tweet_count_list.append(d)
        except Exception as e:
            print(e)
    tweet_counts = pd.DataFrame(tweet_count_list)
    return tweet_counts


def store_tweet_counts(tweet_counts=None, update_ts=None):
    """
    Store tweet counts in the tweetcounts table.
    """
    if tweet_counts is None:
        tweet_counts = get_tweet_counts()
    if update_ts is None:
        update_ts = datetime.datetime.now()
    ul_df = tweet_counts.copy()
    ul_df['update_ts'] = update_ts
    engine = sqlalchemy.create_engine(
        'postgresql+psycopg2://{username:s}:{password:s}'
        '@{host:s}:{port:.0f}/{database:s}'
        .format(username=authapi.pgdb.username,
                password=authapi.pgdb.password,
                host='localhost',
                port=5432,
                database=authapi.pgdb.db_name))
    ul_df.to_sql('tweetcounts', engine, if_exists='append',index=False)
