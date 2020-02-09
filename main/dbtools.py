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
    return pd.read_sql(sql=sql, con=con)


def insert(df, name, con=PI_PROD):
    df.to_sql(name, con=con, if_exists='append', index=False)


def get_twitter_users_db(con=PI_PROD):
    """
    Return a list of twitter users present in the database.
    """
    q = 'SELECT "user" FROM tweetcounts GROUP BY "user"'
    twitter_users_global = select(q)
    twitter_users_global = twitter_users_global['user'].tolist()
