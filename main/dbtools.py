import authapi
import sqlalchemy
import pandas as pd
from dataclasses import dataclass


@dataclass
class DataBaseEngine():
    def __init__(self, credentials):
        username: str
        password: str
        database: str
        host: str
        port: int


con_str = r'postgresql+psycopg2://{username:s}:{password:s}'\
          r'@{host:s}:{port:.0f}/{database:s}'

prod_conn_str = con_str.format(**authapi.pgdb_prod.__dict__)
dev_conn_str = con_str.format(**authapi.pgdb_dev.__dict__)

prod_engine = sqlalchemy.create_engine(prod_conn_str)
dev_engine = sqlalchemy.create_engine(dev_conn_str)

test_q = "SELECT * FROM tweetcounts limit 10;"
df = pd.read_sql(sql=test_q, con=prod_engine)

def store_pi_df(pi_df=None, update_ts=None):
    """
    Store the PredictIt API data in the PiApi table.
    """
    if pi_df is None:
        pi_df = get_pi_df()
    if update_ts is None:
        update_ts = datetime.datetime.now()
    ul_df = pi_df.copy()
    ul_df['update_ts'] = update_ts

    ul_df.to_sql('piapi', engine, if_exists='append', index=False)