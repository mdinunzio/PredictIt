import pandas as pd
import predictit
import twitter
import authapi
import datetime
import sqlalchemy
import time
from threading import Thread


twitter_users = predictit.get_twitter_users()


def store_continuously():
    while True:
        try:
            print(datetime.datetime.now())
            print('\tStoring')
            tweet_counts = twitter.get_tweet_counts(twitter_users)
            store_tweet_counts(tweet_counts)
            print('\tSuccess')
        except Exception as e:
            print(e)
        time.sleep(60)


def main():
    t = Thread(target=store_continuously, daemon=True)
    t.start()
