from predictit import PiEngine
import dbtools as dbt
import datetime


pie = PiEngine(authenticate=True)

market_meta = pie.get_market_meta(market_id=5914)
market_meta = market_meta.to_frame().T
market_meta['update_ts'] = datetime.datetime.now()

dbt.insert(market_meta, name='pimarketmeta', con=dbt.PI_DEV)
