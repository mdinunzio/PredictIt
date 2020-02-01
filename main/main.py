import pandas as pd
import predictit
import twitter
import authapi
import datetime
import sqlalchemy
import time
from threading import Thread


def run_main():
    while True:
        try:
            update_ts = datetime.datetime.now()
            print(update_ts)
            print('Pulling data')
            pi_data = predictit.get_pi_data()
            pi_df = predictit.get_pi_df(pi_data=pi_data)
            # TODO get prior DB users
            twitter_users = predictit.get_twitter_users(pi_data)
            tweet_counts = twitter.get_tweet_counts(twitter_users)
            print('Storing data')
            predictit.store_pi_df(pi_df, update_ts)
            twitter.store_tweet_counts(tweet_counts, update_ts)
            print('\tSuccess')
        except Exception as e:
            print(e)
        time.sleep(60)  # TODO make this dynamic


if __name__ == "__main__":
    t = Thread(target=run_main, daemon=True)
    t.start()
