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
USR_DIR = os.environ['USERPROFILE']
DESKTOP = os.path.join(USR_DIR, 'Desktop')

# Twitter
auth = tweepy.OAuthHandler(authapi.twitter.api_key,
                           authapi.twitter.api_secret_key)
auth.set_access_token(authapi.twitter.access_token,
                      authapi.twitter.access_token_secret)
twitter_api = tweepy.API(auth)


# MAIN #######################################################################

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


def get_pi_markets(pi_data=None):
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


def get_pi_contracts(pi_data=None):
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


def get_low_risk(threshold=.99, contracts=None, export=False):
    """
    Return a DataFrame of lower-risk contract opportunities.
    """
    if contracts is None:
        contracts = get_pi_contracts()
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
        contracts = get_pi_contracts()
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


def get_twitter_markets(pi_data=None):
    """
    Return a DataFrame of tweet markets.
    """
    markets = get_pi_markets(pi_data)
    twitter_markets = markets[markets['market'].str.contains('tweets')]
    return twitter_markets


def get_twitter_users(pi_data=None):
    """
    Return a list of Twitter users listed within the PredictIt data.
    """
    twitter_markets = get_twitter_markets(pi_data)
    twitter_users = twitter_markets['market'].map(
        lambda x: x.split(' ')[0].replace('@', ''))
    twitter_users = twitter_users.tolist()
    return twitter_users
    

def get_tweet_counts(twitter_users=None):
    """
    Return a DataFrame of tweet counts for a given list of users.
    """
    if twitter_users is None:
        twitter_users = get_twitter_users()
    tweet_count_list = []
    for user in twitter_users:
        try:
            api_user = twitter_api.get_user(user)
            tweet_count = api_user.statuses_count
            d = {'user': user,
                 'tweets' : tweet_count}
            tweet_count_list.append(d)
        except Exception as e:
            print(e)
    tweet_counts = pd.DataFrame(tweet_count_list)
    return tweet_counts
