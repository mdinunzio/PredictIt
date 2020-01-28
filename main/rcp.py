import pandas as pd
import urllib3
from bs4 import BeautifulSoup


# Pandas
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


RCP_URL = r'https://www.realclearpolitics.com/epolls/other/president_trump_job_approval-6179.html#polls'
http = urllib3.PoolManager()
response = http.request('GET', RCP_URL)

data_enc = response.data
data_str = data_enc.decode('utf-8')

soup = BeautifulSoup(data_str)

table = soup.find(name='table', class_='large')
rows = table.find_all('tr')

headers = rows.pop(0)
columns = [x.get_text() for x in headers]

data = [[td.get_text() for td in row] for row in rows]

df = pd.DataFrame(columns=columns, data=data)