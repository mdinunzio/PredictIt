from predictit import PiEngine
import dbtools as dbt
import datetime
import pandas as pd
import time


pie = PiEngine(authenticate=True)

market_meta = pie.get_market_meta(market_id=5914)
market_meta = market_meta.to_frame().T
market_meta['update_ts'] = datetime.datetime.now()

dbt.insert(market_meta, name='pimarketmeta', con=dbt.PI_DEV)

q = "SELECT DISTINCT id_market FROM piapi"
existing_market_ids = dbt.select(q, con=dbt.PI_PROD)
existing_market_ids = existing_market_ids['id_market'].tolist()

q = "SELECT DISTINCT market_id FROM pimarketmeta"
meta_market_ids = dbt.select(q, con=dbt.PI_DEV)
meta_market_ids = meta_market_ids['market_id'].tolist()

grab_ids = list(set(existing_market_ids) - set(meta_market_ids))

for i, mid in enumerate(grab_ids):
    try:
        print(i, mid)
        market_meta = pie.get_market_meta(market_id=mid)
        market_meta = market_meta.to_frame().T
        market_meta['update_ts'] = datetime.datetime.now()
        dbt.insert(market_meta, name='pimarketmeta', con=dbt.PI_DEV)
        time.sleep(2)
        if i % 30 == 0:
            time.sleep(10)
    except Exception as e:
        print(e)
        break

mm_dev = dbt.select('SELECT * FROM pimarketmeta', con=dbt.PI_DEV)
dbt.insert(mm_dev, 'pimarketmeta', dbt.PI_PROD)

