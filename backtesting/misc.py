import dbtools as dbt
import datetime
import matplotlib.pyplot as plt


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

d = df[df['user']=='realDonaldTrump']
d = df[df['user']=='AOC']

rdt_q  = """
SELECT * FROM tweetcounts
WHERE "user" = 'realDonaldTrump'
"""

df = dbt.select(rdt_q, con=dbt.PI_PROD)
df['prevt'] = df['tweets'].shift(1)
df = df[df['tweets']!=df['prevt']]

plt.scatter(df['update_ts'], df['tweets'])
plt.savefig(r'C:\Users\mdinu\Desktop\one.png')

df2 = df
df2['date'] = df2['update_ts'].map(lambda x: x.to_pydatetime().date())

df2 = df.groupby('date').nth(-1)
df2 = df2.reset_index()
df2['days'] = df2.index.tolist()

plt.figure()
plt.scatter(df2['days'], df2['tweets'])
plt.savefig(r'C:\Users\mdinu\Desktop\two.png')
