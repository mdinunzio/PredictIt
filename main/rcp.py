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

data_list = []
for row in rows:
    row_list = []
    for td in row.find_all('td'):
        if len(td) > 1:
            txt = list(td.children)[0].get_text()
        else:
            txt = td.get_text()
        row_list.append(txt)
    data_list.append(row_list)

df = pd.DataFrame(columns=columns, data=data_list)
