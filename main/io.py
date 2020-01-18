import pandas as pd
import urllib3
import json
import datetime


pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

URL = r'https://www.predictit.org/api/marketdata/all/'


def fix_dates(x):
    """
    Return the appropriate datetime object for dateEnd column information.
    """
    fmt = r'%Y-%m-%dT%H:%M:%S'
    if x == 'N/A' or x == 'NA':
        return pd.NaT
    elif pd.isnull(x):
        return x
    else:
        return datetime.datetime.strptime(x, fmt)


def get_contracts():
    """
    Return a DataFrame of formatted contract data.
    """
    http = urllib3.PoolManager()
    response = http.request('GET', URL)

    data_enc = response.data
    data_str = data_enc.decode('utf-8')

    data = json.loads(data_str)
    markets = data['markets']

    contract_list = []

    for mkt in markets:
        c = pd.DataFrame(mkt['contracts'])
        c['marketId'] = mkt['id']
        c['market'] = mkt['shortName']
        c['updateTime'] = mkt['timeStamp']
        c['url'] = mkt['url']
        contract_list.append(c)

    contracts = pd.concat(contract_list)
    contracts = contracts.reset_index(drop=True)
    c_cols = ['market', 'shortName', 'bestBuyYesCost', 'bestBuyNoCost',
              'lastTradePrice', 'lastClosePrice', 'marketId',
              'updateTime', 'url']
    contracts = contracts[c_cols]
    c_map = {'shortName': 'contract', 'bestBuyYesCost': 'yes',
             'bestBuyNoCost': 'no', 'lastTradePrice': 'last', 
             'lastClosePrice': 'close'}
    contracts = contracts.rename(columns=c_map)
    contracts['dateEnd'] = contracts['dateEnd'].map(fix_dates)
    contracts['updateTime'] = contracts['updateTime'].map(
        lambda x: datetime.datetime.strptime(x[:-3], '%Y-%m-%dT%H:%M:%S.%f'))
    return contracts

