import predictit
import twitter
import datetime
import time
import dbtools as dbt
from threading import Thread
import re


# SETUP ######################################################################

pie = predictit.PiEngine(authenticate=False)
twitter_users_global = dbt.get_twitter_users_db()


# HELPER FUNCTIONS ###########################################################

def get_twitter_markets(api_df):
    """
    Return a DataFrame of tweet markets.
    """
    twitter_markets = api_df[api_df['name_market'].str.contains('tweets')]
    twitter_markets = twitter_markets['name_market'].unique().tolist()
    return twitter_markets


def get_twitter_users(api_df):
    """
    Return a list of Twitter users listed within the PredictIt data.
    """
    twitter_markets = get_twitter_markets(api_df)
    twitter_users = [x.split('@')[1].split(' ')[0]
                     for x in twitter_markets]
    twitter_users = list(set(twitter_users))
    return twitter_users


# MAIN FUNCTIONALITY #########################################################

def run_main():
    """
    Continuously pull and upload data.
    """
    global twitter_users_global
    while True:
        try:
            update_ts = datetime.datetime.now()
            print(update_ts)
            print('\tPulling data')
            pie.update_api_df()
            twitter_users = predictit.get_twitter_users(pi_data)
            twitter_users_global = list(set(twitter_users +
                                            twitter_users_global))
            tweet_counts = twitter.get_tweet_counts(twitter_users_global)
            print('\tStoring data')
            predictit.store_pi_df(pi_df, update_ts)
            twitter.store_tweet_counts(tweet_counts, update_ts)
            print('\tSuccess')
        except Exception as e:
            print(e)
        time.sleep(60)  # TODO make this dynamic


if __name__ == "__main__":
    init_globals()
    t = Thread(target=run_main, daemon=True)
    t.start()
