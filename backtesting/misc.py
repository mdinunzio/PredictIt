import dbtools as dbt
import datetime
import matplotlib.pyplot as plt
import pandas as pd


eod_tweets_q = """
SELECT lhs.update_ts::DATE as date, rhs.user, rhs.tweets, lhs.update_ts
FROM (
    (SELECT MAX(update_ts) as update_ts
    FROM tweetcounts
    GROUP BY update_ts::DATE
    ORDER BY update_ts::DATE) lhs
    LEFT JOIN
    (SELECT * FROM tweetcounts) rhs
    ON lhs.update_ts = rhs.update_ts)
"""

df = dbt.select(eod_tweets_q)
del(df['update_ts'])
df = df.sort_values(['date', 'user'])
df = df.reset_index(drop=True)

today = datetime.date.today()
min_date = df['date'].min()
max_date = df['date'].max()

date_range = pd.date_range(min_date, max_date)
date_range = [x.date() for x in date_range]
lhs = pd.DataFrame(columns=['date'], data=date_range)

df = pd.merge(lhs, df, on='date', how='left')
df = df[df['date']!=today]

df = df.sort_values(['user', 'date'])
df = df.reset_index(drop=True)

df['tweetsPrev'] = df.groupby(['user'])['tweets'].shift(1)
df['tweetChg'] = df['tweets'] - df['tweetsPrev']
df['day'] = df['date'].map(lambda x: f'{x:%a}')
df = df.dropna(subset=['tweetChg'])

grp = df.groupby(['user', 'day'])
stats = grp[['tweetChg']].agg(['mean', 'std', 'count'])
