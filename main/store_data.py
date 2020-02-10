import predictit
import twitter
import datetime
import time
import dbtools as dbt
from threading import Thread


# SETUP ######################################################################

con = dbt.PI_PROD

pie = predictit.PiEngine(authenticate=False)
twitter_users_global = dbt.get_twitter_users()


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

def store_api_and_tweets():
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
            twitter_users = get_twitter_users(pie.api_df)
            twitter_users_global = list(
                set(twitter_users + twitter_users_global))
            tweet_counts = twitter.get_tweet_counts(twitter_users_global)
            print('\tStoring data')
            dbt.store_pi_api(pie.api_df, update_ts, con)
            dbt.store_tweet_counts(tweet_counts, update_ts, con)
            print('\tSuccess')
        except Exception as e:
            print(e)
        pi_ts = pie.api_df['predictit_ts'].max().to_pydatetime()
        next_pi_ts = pi_ts + datetime.timedelta(seconds=60)
        now = datetime.datetime.now()
        delay = (next_pi_ts - now).total_seconds()
        if delay <= 0 or delay > 60:
            delay = 60
        else:
            delay = delay + 10
        print(f'\tSleeping {delay:.0f} seconds')
        time.sleep(delay)


if __name__ == "__main__":
    t = Thread(target=store_api_and_tweets, daemon=False)
    t.start()
