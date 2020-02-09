import authapi
import datetime
import sqlalchemy
from dataclasses import dataclass


@dataclass
class DataBaseConnection:
    username: str
    password: str
    database: str
    host: str
    port: int


engine = sqlalchemy.create_engine(
    f'postgresql+psycopg2://{username:s}:{password:s}'
    f'@{host:s}:{port:.0f}/{database:s}').format(
            username=authapi.pgdb.username,
            password=authapi.pgdb.password,
            host='localhost',
            port=5432,
            database=authapi.pgdb.db_name))

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