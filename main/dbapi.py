from collections import namedtuple
import pandas as pd
import authapi
import externapi
import datetime
import sqlalchemy
import time
from threading import Thread


twitter_users = externapi.get_twitter_users()


def store_tweet_counts(tweet_counts, update_ts=None):
    engine = sqlalchemy.create_engine(
        'postgresql+psycopg2://{username:s}:{password:s}'
        '@{host:s}:{port:.0f}/{database:s}'
        .format(username=authapi.pgdb.username,
                password=authapi.pgdb.password,
                host='localhost',
                port=5432,
                database=authapi.pgdb.db_name))
    if update_ts is None:
        update_ts = datetime.datetime.now()
    tweet_counts['update_ts'] = update_ts
    tweet_counts.to_sql('tweetcounts', engine, if_exists='append',index=False)


def store_continuously():
    while True:
        try:
            print(datetime.datetime.now())
            print('\tStoring')
            tweet_counts = externapi.get_tweet_counts(twitter_users)
            store_tweet_counts(tweet_counts)
            print('\tSuccess')
        except Exception as e:
            print(e)
        time.sleep(60)


def main():
    t = Thread(target=store_continuously, daemon=True)
    t.start()
