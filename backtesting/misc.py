import dbtools as dbt
import datetime



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
df['tweetsPrev'] = df.groupby(['user'])['tweets'].shift(1)
df['tweetChg'] = df['tweets'] - df['tweetsPrev']
df['day'] = df['date'].map(lambda x: f'{x:%a}')

rdt = df[df['user']=='realDonaldTrump']