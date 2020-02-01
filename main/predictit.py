import pandas as pd
import urllib3
import json
import datetime
import os
import tweepy
import authapi


# SETUP ######################################################################

# Pandas
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

# URLs and directories
PI_URL = r'https://www.predictit.org/api/marketdata/all/'
PI_MKT_URL = r'https://www.predictit.org/api/Market'
USR_DIR = os.environ['USERPROFILE']
DESKTOP = os.path.join(USR_DIR, 'Desktop')


# HELPER FUNCTIONS ###########################################################

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


# MAIN #######################################################################

def get_pi_data():
    """
    Returns a JSON-style dictionary of PredictIt.org API data.
    """
    http = urllib3.PoolManager()
    response = http.request('GET', PI_URL)

    data_enc = response.data
    data_str = data_enc.decode('utf-8')

    pi_data = json.loads(data_str)
    return pi_data


def unpack_pi_data(pi_data=None):
    """
    Return a DataFrame of all PredictIt data.
    """
    if pi_data is None:
        pi_data = get_pi_data()
    markets = pi_data['markets']
    pi_list = []

    for mkt in markets:
        m_df = pd.DataFrame(mkt).drop('contracts', axis=1)
        c_df = pd.DataFrame(mkt['contracts'])
        mc_df = pd.merge(m_df, c_df, left_index=True, right_index=True,
                         suffixes=('Market', 'Contract'))
        pi_list.append(mc_df)
    pi_df = pd.concat(pi_list)
    return pi_df
    


def get_markets(pi_data=None):
    """
    Return a DataFrame of formatted market data.
    """
    if pi_data is None:
        pi_data = get_pi_data()
    market_data = pi_data['markets']
    markets = pd.DataFrame(data=market_data)
    col_map = {'id': 'marketId', 'shortName': 'market'}
    markets = markets.rename(columns=col_map)
    drop_cols = ['name', 'image', 'contracts']
    markets = markets.drop(drop_cols, axis=1)
    return markets


def get_contracts(pi_data=None):
    """
    Return a DataFrame of formatted contract data.
    """
    if pi_data is None:
        pi_data = get_pi_data()
    markets = pi_data['markets']

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
              'lastTradePrice', 'lastClosePrice', 'dateEnd', 'updateTime',
              'marketId', 'url']
    contracts = contracts[c_cols]
    c_map = {'shortName': 'contract', 'bestBuyYesCost': 'yes',
             'bestBuyNoCost': 'no', 'lastTradePrice': 'last', 
             'lastClosePrice': 'close'}
    contracts = contracts.rename(columns=c_map)
    contracts['dateEnd'] = contracts['dateEnd'].map(fix_dates)
    contracts['updateTime'] = contracts['updateTime'].map(
        lambda x: datetime.datetime.strptime(x[:-3], '%Y-%m-%dT%H:%M:%S.%f'))
    return contracts


def get_twitter_markets(pi_data=None):
    """
    Return a DataFrame of tweet markets.
    """
    markets = get_markets(pi_data)
    twitter_markets = markets[markets['market'].str.contains('tweets')]
    return twitter_markets


def get_twitter_users(pi_data=None):
    """
    Return a list of Twitter users listed within the PredictIt data.
    """
    twitter_markets = get_twitter_markets(pi_data)
    twitter_users = twitter_markets['market'].map(
        lambda x: x.split(' ')[0].replace('@', ''))
    twitter_users = twitter_users.unique().tolist()
    return twitter_users


def get_market_meta(market_id):
    """
    Return a DataFrame of parsed market infomration including rules
    and other specifics.
    """
    http = urllib3.PoolManager()
    mkt_url = os.path.join(PI_MKT_URL, '{:.0f}'.format(market_id))
    response = http.request('GET', mkt_url)

    data_enc = response.data
    data_str = data_enc.decode('utf-8')

    mkt_data = json.loads(data_str)
    mkt_df = pd.Series(mkt_data)
    return mkt_df


def get_order_book(contract_id):
    """
    Return the order book for a given contract.
    """
    http = urllib3.PoolManager()
    headers = {'Accept': 'application/json, text/plain, */*',
               'Accept-Encoding': 'gzip, deflate, br',
               'Accept-Language': 'en-US,en;q=0.9,it;q=0.8',
               'Authorization': 'AUTH HERE',
               'Connection': 'keep-alive',
               'Cookie': 'COOKIE HERE',
               'Host': 'www.predictit.org',
               'Referer': 'https://www.predictit.org/markets/detail/6371/How-many-tweets-will-@mike_pence-post-from-noon-Jan-31-to-Feb-7',
               'Sec-Fetch-Mode': 'cors',
               'Sec-Fetch-Site': 'same-origin',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'}
    response = http.request('GET', 'https://www.predictit.org/api/Trade/20757/OrderBook', headers=headers)
    data_enc = response.data
    data_str = data_enc.decode('utf-8')
    ob_data = json.loads(data_str)
    yes_ob_data = ob_data['yesOrders']
    no_ob_data = ob_data['noOrders']
    yes_ob_df = pd.DataFrame(yes_ob_data)
    no_ob_df = pd.DataFrame(no_ob_data)
    ob_df = pd.concat([yes_ob_df, no_ob_df])
    ob_df = ob_df.reset_index(drop=True)
    return ob_df


def get_low_risk(threshold=.99, contracts=None, export=False):
    """
    Return a DataFrame of lower-risk contract opportunities.
    """
    if contracts is None:
        contracts = get_contracts()
    low_risk = contracts[(contracts['yes'] >= threshold) |
                         (contracts['no'] >= threshold)]
    low_risk = low_risk.sort_values('dateEnd')
    low_risk = low_risk.reset_index(drop=True)
    if export:
        low_risk.to_excel(os.path.join(DESKTOP, 'low risk.xlsx'), index=False)
    return low_risk


def get_neg_risk(contracts=None, export=False):
    """
    Return a DataFrame with negative-risk calculations.
    """
    if contracts is None:
        contracts = get_contracts()
    risk = contracts.copy()
    risk_grp = risk.groupby('marketId')
    risk['no payout'] = 1 - risk['no']
    risk['risk'] = risk_grp['no payout'].transform('sum')
    risk = risk.sort_values(['risk', 'marketId'], ascending=[False, True])
    risk = risk.reset_index(drop=True)
    if export:
        risk.to_excel(os.path.join(DESKTOP, 'negative risk.xlsx'),
                      index=False)
    return risk
