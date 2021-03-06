import authapi
import sqlalchemy
import pandas as pd
import datetime


# SETUP ######################################################################

con_str = r'postgresql+psycopg2://{username:s}:{password:s}'\
          r'@{host:s}:{port:.0f}/{database:s}'

prod_conn_str = con_str.format(**authapi.pgdb_prod.__dict__)
dev_conn_str = con_str.format(**authapi.pgdb_dev.__dict__)

PI_PROD = sqlalchemy.create_engine(prod_conn_str)
PI_DEV = sqlalchemy.create_engine(dev_conn_str)

test_q = "SELECT * FROM tweetcounts limit 10;"
df = pd.read_sql(sql=test_q, con=PI_PROD)


# MAIN FUNCTIONALITY #########################################################

def select(sql, con=PI_PROD):
    """
    Return a DataFrame from a select query.
    """
    return pd.read_sql(sql=sql, con=con)


def insert(df, name, con=PI_PROD):
    """
    Insert a DataFrame into the specified database table.
    """
    df.to_sql(name, con=con, if_exists='append', index=False)


def get_twitter_users(con=PI_PROD):
    """
    Return a list of twitter users present in the database.
    """
    q = 'SELECT "user" FROM tweetcounts GROUP BY "user"'
    twitter_users = select(q, con=con)
    twitter_users = twitter_users['user'].tolist()
    return twitter_users


def get_market_meta(market_ids, con=PI_PROD):
    """
    Return a DataFrame of market metadata for the list of
    given market ids.
    """
    q = """
    SELECT * FROM pimarketmeta
    WHERE market_id IN ({:s})
    """.format(', '.join([str(x) for x in market_ids]))
    market_meta = select(q, con=con)
    return market_meta


def store_tweet_counts(tweet_counts, update_ts, con=PI_PROD):
    """
    Insert the tweet_counts DataFrame into the tweetcounts database.
    """
    tweet_counts['update_ts'] = update_ts
    insert(tweet_counts, 'tweetcounts', con=con)


def store_pi_api(api_df, update_ts, con=PI_PROD):
    """
    Insert the tweet_counts DataFrame into the tweetcounts database.
    """
    api_df['update_ts'] = update_ts
    insert(api_df, 'piapi', con=con)

