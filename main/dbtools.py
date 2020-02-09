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
    return pd.read_sql(sql=test_q, con=PI_PROD)


def insert(df, name, con=PI_PROD):
    df.to_sql(name, con=con, if_exists='append', index=False)


def store_pi_df(pi_df, update_ts=None):
    """
    Store the PredictIt API data in the PiApi table.
    """
    if update_ts is None:
        update_ts = datetime.datetime.now()
    ul_df = pi_df.copy()
    ul_df['update_ts'] = update_ts
    insert(ul_df, 'piapi')
