from collections import namedtuple
import pandas as pd
import authapi
import externapi
import datetime
import psycopg2


twitter_users = externapi.get_twitter_users()
tweet_counts = externapi.get_tweet_counts(twitter_users)

def store_tweet_counts(tweet_counts):
    tweet_counts['update_ts'] = datetime.datetime.now()