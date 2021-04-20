import os
import re
from time import sleep
from datetime import datetime, timedelta, date
import pandas as pd

import joblib

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

grs = joblib.load('ground_truth_grs.joblib')
grs.update(joblib.load('other_grs.joblib'))

base = 'https://www.gismeteo.ru/diary/{gm_code}/{year}/{month}'

last_month = datetime.now().replace(day=1) - timedelta(days=1)

# install chrome driver
try:
    driver = webdriver.Chrome(ChromeDriverManager().install())
except:
    driver = webdriver.Chrome("/usr/bin/chromedriver",chrome_options=chrome_options)

from tqdm import tqdm
dfs = []
for code, v in tqdm(grs.items()):
    # get i page
    driver.get(base.format(gm_code=v[0], year=last_month.year, month=last_month.month))
    sleep(1)
    
    # grab html
    generated_html = driver.page_source
    #generated_html = re.sub('<img src=\"//(.+)\.png\" class=\".+\">', '\\1', generated_html)

    df = pd.read_html(generated_html)[0]
    df['code'] = code
    df['month'] = last_month.month
    df['year'] = last_month.year
    
    dfs.append(df.copy())
            

dff = pd.concat(dfs).reset_index(drop=True)

dfn = pd.DataFrame(
    dff.values,
    columns=['monthday', 'day_t', 'day_p','day_cloud', 'day_events', 'day_wind',
             'night_t', 'night_p', 'night_cloud', 'night_events', 'night_wind',
             'code', 'month', 'year']
    )

dfn['date'] = dfn.apply(lambda x: date(int(x['year']), int(x['month']), int(x['monthday'])), axis=1)
dfn = dfn.drop(['year', 'month', 'monthday'], axis=1)

dfn['day_wind_side'] = dfn['day_wind'].fillna('').apply(lambda x: x.split()[0] if x else None)
dfn['night_wind_side'] = dfn['night_wind'].fillna('').apply(lambda x: x.split()[0] if x else None)
dfn['day_wind'] = dfn['day_wind'].fillna('').apply(lambda x: ''.join(re.findall('\d+', x)) if x else None)
dfn['night_wind'] = dfn['night_wind'].fillna('').apply(lambda x: ''.join(re.findall('\d+', x)) if x else None)

dfn.to_csv('data/past.tsv', sep='\t', index=False)
