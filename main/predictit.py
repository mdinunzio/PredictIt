import pandas as pd
import urllib3
import json
import datetime
import os
import tweepy
import authapi
import re
import sqlalchemy
import getpass
import requests


# SETUP ######################################################################

# Pandas
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

# Directories
USR_DIR = os.environ['USERPROFILE']
DESKTOP = os.path.join(USR_DIR, 'Desktop')

# URLS
PI_URL = r'https://www.predictit.org'

# Regex
_camel_pattern = re.compile(r'(?<!^)(?=[A-Z])')


# HELPER FUNCTIONS ###########################################################

def to_timetype(x, datetime_=False):
    """
    Return the appropriate datetime object for dateEnd column information.
    """
    if x == 'N/A' or x == 'NA':
        return pd.NaT
    elif pd.isnull(x):
        return x
    else:
        ts = pd.Timestamp(x)
    if not datetime_:
        return ts
    else:
        return ts.to_pydatetime()


def to_snake(x):
    """
    Return a string in snake case.
    """
    return _camel_pattern.sub('_', x).lower()


# MODELS ####################################################################

class PiEngine():
    """
    An engine for interacting with PredictIt's non-API functionality and data.
    """

    trade_to_int = {'buy no': 0,
                    'buy yes': 1,
                    'sell no': 2,
                    'sell yes': 3}

    int_to_trade = {0: 'buy no',
                    1: 'buy yes',
                    2: 'sell no',
                    3: 'sell yes'}

    def __init__(self, max_quantity=850):
        self.email = authapi.predictit.email
        self.password = authapi.predictit.password
        if self.password == '':
            self.password = getpass.getpass('Enter PI Password:')
        self.max_quantity = min(max_quantity, 850)
        self.max_timeouts = 5
        self.response = None
        self.authenticate_session()
        self.update_book()
        self.update_open_orders()

    def authenticate_session(self):
        """
        Initiate and authenticate requests session.
        """
        self.session = requests.Session()
        self.session.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9,it;q=0.8',
            'Connection': 'keep-alive',
            'Host': 'www.predictit.org',
            'Referer': 'https://www.predictit.org',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/79.0.3945.130 Safari/537.36'}
        self.response = self.session.post(
            f'{PI_URL}/api/Account/token',
            data={'email': self.email, 'password': self.password,
                  'grant_type': 'password', 'rememberMe': 'true'})
        if not self.response:
            print('Not Authenticated')
        token = self.response.json()['access_token']
        self.session.headers['Authorization'] = 'Bearer ' + token
        print('Authenticated')

    def _make_safe_request(self, request_type, *args, **kwargs):
        """
        Return and store a requests response using current session,
        re-authenticating if necessary.
        """
        timeout_counter = 0
        request_fn = getattr(self.session, request_type)
        while timeout_counter < self.max_timeouts:
            response = request_fn(*args, **kwargs)
            status_code = response.status_code
            if status_code != 401:
                break
            self.authenticate_session()
            timeout_counter += 1
        self.response = response
        return response

    def get(self, *args, **kwargs):
        """
        Return and store a get request response re-authenticating
        if necessary.
        """
        return self._make_safe_request('get', *args, **kwargs)

    def post(self, *args, **kwargs):
        """
        Return and store a post request response re-authenticating
        if necessary.
        """
        return self._make_safe_request('post', *args, **kwargs)

    def get_quotes(self, contract_id):
        rsrc_url = f'{PI_URL}/api/Trade/{contract_id:.0f}/OrderBook'
        quote_data = self.get(rsrc_url).json()
        yes_qts_data = quote_data['yesOrders']
        no_qts_data = quote_data['noOrders']
        yes_qts_df = pd.DataFrame(yes_qts_data)
        no_qts_df = pd.DataFrame(no_qts_data)
        qts_cols_mrg = ['pricePerShare', 'quantity']
        qts_cols_fnl = ['contractId', 'quantityYes',
                        'pricePerShareYes', 'pricePerShareNo',
                        'quantityNo']
        if len(yes_qts_df) > 0 and len(no_qts_df) > 0:
            quotes = pd.merge(left=yes_qts_df[qts_cols_mrg],
                              right=no_qts_df[qts_cols_mrg],
                              left_index=True,
                              right_index=True,
                              how='outer',
                              suffixes=('Yes', 'No'))
            quotes['contractId'] = contract_id
        quotes = quotes[qts_cols_fnl]
        qts_map = {'quantityYes': 'qtyYes',
                   'quantityNo': 'qtyNo',
                   'pricePerShareYes': 'pxYes',
                   'pricePerShareNo': 'pxNo'}
        quotes = quotes.rename(columns=qts_map)
        quotes = quotes.rename(columns=to_snake)
        return quotes

    def update_book(self):
        rsrc_url = f'{PI_URL}/api/Profile/Shares'
        response = self.get(rsrc_url)
        book_data = response.json()
        markets = book_data['markets']
        book_list = []
        for market in markets:
            m_df = pd.DataFrame(market).drop('marketContracts', axis=1)
            c_df = pd.DataFrame(market['marketContracts'])
            mc_df = pd.merge(m_df, c_df,
                             left_index=True, right_index=True,
                             suffixes=('Market', 'Contract'))
            book_list.append(mc_df)
        book = pd.concat(book_list)
        book = book.reset_index(drop=True)
        book['edge'] = book.apply(
            lambda x:
            x['bestYesPrice'] - x['userAveragePricePerShare']
            if x['userPrediction'] else
            x['bestNoPrice'] - x['userAveragePricePerShare'],
            axis=1)
        book['pl'] = book['edge'] * book['userQuantity']
        book_cols = \
            ['marketShortName', 'contractName', 'userPrediction',
             'userQuantity', 'userAveragePricePerShare',
             'bestYesPrice', 'bestNoPrice', 'edge', 'pl',
             'userOpenOrdersBuyQuantity', 'userOpenOrdersSellQuantity',
             'lastTradePrice', 'lastClosePrice', 'marketSharesTraded',
             'marketId', 'contractId']
        book_map = \
            {'marketShortName': 'market', 'contractName': 'contract',
             'userPrediction': 'pred', 'userQuantity': 'shares',
             'userAveragePricePerShare': 'vwap',
             'userOpenOrdersBuyQuantity': 'openBuys',
             'userOpenOrdersSellQuantity': 'openSells',
             'bestYesPrice': 'bestYes', 'bestNoPrice': 'bestNo',
             'lastTradePrice': 'last', 'lastClosePrice': 'close',
             'marketSharesTraded': 'mktVolume'}
        book = book[book_cols]
        book = book.rename(columns=book_map)
        book = book.rename(columns=to_snake)
        self.book = book

    def update_open_orders(self):
        """
        Update the open_orders attribute.
        Must run update_book beforehand for most up-to-date results.
        """
        open_df = self.book[self.book[['open_buys', 'open_sells']].any(axis=1)]
        open_contracts = open_df['contract_id'].unique().tolist()
        contract_list = []
        for cid in open_contracts:
            rsrc_url = f'{PI_URL}/api/Profile/contract/{cid}/Offers'
            response = self.get(rsrc_url)
            cd_df = pd.DataFrame(response.json()).drop('offers', axis=1)
            o_df = pd.DataFrame(response.json()['offers'])
            oc_df = pd.merge(left=cd_df, right=o_df,
                             left_index=True, right_index=True,
                             suffixes=('', 'Offer'))
            contract_list.append(oc_df)
        oo_cols = ['contractName', 'tradeType', 'pricePerShare',
                   'quantity', 'remainingQuantity', 'dateCreated',
                   'contractId', 'offerId']
        if len(contract_list) == 0:
            open_orders = pd.DataFrame(columns=oo_cols)
        else:
            open_orders = pd.concat(contract_list)
        open_orders = open_orders[oo_cols]
        oo_map = {'contractName': 'contract', 'tradeType': 'type',
                  'pricePerShare': 'price',
                  'quantity': 'qty',
                  'remainingQuantity': 'left',
                  'dateCreated': 'entry_ts'}
        open_orders = open_orders.rename(columns=oo_map)
        open_orders = open_orders.rename(columns=to_snake)
        open_orders['type'] = open_orders['type'].map(self.int_to_trade)
        open_orders['entry_ts'] = open_orders['entry_ts'].map(to_timetype)
        self.open_orders = open_orders

    def place_order(self, contract_id, trade_type, quantity, price):
        """
        Place an order on PredictIt.com.
        Valid trade types are buy_no, buy_yes, sell_no, and sell_yes.
        You can only sell when you are long shares, and therefore
        """
        trade_type = trade_type.lower()
        price = float(price)
        if trade_type not in self.trade_map:
            raise ValueError('Invalid trade type')
        if quantity > self.max_quantity:
            raise ValueError(
                f'{quantity} exceeds maximum quantity of {self.max_quantity}')
        if price < 1 or price > 99:
            raise ValueError('Price must be between 1 and 99')
        if not price.is_integer():
            raise ValueError('Price must be integer between 1 and 99')
        rsrc_url = f'{PI_URL}/api/Trade/SubmitTrade'
        data = {'quantity': quantity,
                'pricePerShare': price,
                'contractId': contract_id,
                'tradeType': trade_type}
        response = self.post(rsrc_url, data=data)
        response.raise_for_status()
        self.update_book()
        self.update_open_orders()
        print('Order placed')

    def cancel_orders(self, offer_ids):
        self.update_book()
        self.update_open_orders()
        if isinstance(offer_ids, str) and offer_ids.lower() in ('*', 'all'):
            offer_ids = self.open_orders['offer_id'].unique().tolist()
        if isinstance(offer_ids, int) or isinstance(offer_ids, float):
            offer_ids = [offer_ids]
        successes = []
        errors = []
        for offer_id in offer_ids:
            rsrc_url = f'{PI_URL}/api/Trade/CancelOffer/{offer_id}'
            response = self.post(rsrc_url)
            if response:
                successes.append(offer_id)
            else:
                errors.append(offer_id)
        print(f'Cancelled: {len(successes)}/{len(offer_ids)}')
        print(f'Errors:    {len(errors)}/{len(offer_ids)}')
        self.update_book()
        self.update_open_orders()

# MAIN #######################################################################

def get_pi_data():
    """
    Returns a JSON-style dictionary of PredictIt.org API data.
    """
    api_url = r'https://www.predictit.org/api/marketdata/all/'
    http = urllib3.PoolManager()
    response = http.request('GET', api_url)

    data_enc = response.data
    data_str = data_enc.decode('utf-8')

    pi_data = json.loads(data_str)
    return pi_data


def get_pi_df(pi_data=None, refine=True):
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
    pi_df = pi_df.reset_index(drop=True)
    if refine:
        pi_df.columns = [to_snake(x) for x
                         in pi_df.columns]
        col_map = {'time_stamp': 'predictit_ts'}
        pi_df = pi_df.rename(columns=col_map)
        pi_df['predictit_ts'] = pi_df['predictit_ts'].map(to_timetype)
        pi_df['date_end'] = pi_df['date_end'].map(to_timetype)
    return pi_df


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
    engine = sqlalchemy.create_engine(
        'postgresql+psycopg2://{username:s}:{password:s}'
        '@{host:s}:{port:.0f}/{database:s}'
        .format(username=authapi.pgdb.username,
                password=authapi.pgdb.password,
                host='localhost',
                port=5432,
                database=authapi.pgdb.db_name))
    ul_df.to_sql('piapi', engine, if_exists='append',index=False)
    


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
    contracts['dateEnd'] = contracts['dateEnd'].map(to_timetype)
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
    mkt_url = r'https://www.predictit.org/api/Market'
    mkt_url = mkt_url + '{:.0f}'.format(market_id)
    response = http.request('GET', mkt_url)

    data_enc = response.data
    data_str = data_enc.decode('utf-8')

    mkt_data = json.loads(data_str)
    mkt_s = pd.Series(mkt_data)
    return mkt_s


def get_order_book(contract_id):
    """
    Return a Dataframe containing the order book for a given contract.
    """
    http = urllib3.PoolManager()
    headers = {'Accept': 'application/json, text/plain, */*',
               'Accept-Encoding': 'gzip, deflate, br',
               'Accept-Language': 'en-US,en;q=0.9,it;q=0.8',
               'Authorization': authapi.pixhr.authorization,
               'Connection': 'keep-alive',
               'Cookie': authapi.pixhr.cookie,
               'Host': 'www.predictit.org',
               'Referer': 'https://www.predictit.org',
               'Sec-Fetch-Mode': 'cors',
               'Sec-Fetch-Site': 'same-origin',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'}
    ob_url = 'https://www.predictit.org/api/Trade/{:.0f}/OrderBook'
    ob_url = ob_url.format(contract_id)
    response = http.request('GET', ob_url, headers=headers)
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
