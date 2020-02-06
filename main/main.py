import pandas as pd
import predictit
import twitter
import authapi
import datetime
import sqlalchemy
import time
from threading import Thread
import sqlalchemy


# SETUP ######################################################################

# Globals
twitter_users_global = []


# HELPER FUNCTIONS ##########################################################

def init_globals():
    """
    Initialize the global variables used in main functionality.
    """
    global twitter_users_global
    q = 'SELECT "user" FROM tweetcounts GROUP BY "user"'
    engine = sqlalchemy.create_engine(
    'postgresql+psycopg2://{username:s}:{password:s}'
    '@{host:s}:{port:.0f}/{database:s}'
    .format(username=authapi.pgdb.username,
            password=authapi.pgdb.password,
            host='localhost',
            port=5432,
            database=authapi.pgdb.db_name))
    conn = engine.connect()
    res = conn.execute(q)
    usrs = [x[0] for x in res]
    twitter_users_global = usrs

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
            pi_data = predictit.get_pi_data()
            pi_df = predictit.get_pi_df(pi_data=pi_data)
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
