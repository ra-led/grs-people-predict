from time import sleep
from datetime import datetime, timedelta
import pandas as pd

from bs4 import BeautifulSoup
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

#place = 'stavropol'
#code = '5141'
base = 'https://www.gismeteo.ru/weather-{place}-{gm_code}/month/'

try:
    driver = webdriver.Chrome(ChromeDriverManager().install())
except:
    driver = webdriver.Chrome("/usr/bin/chromedriver",chrome_options=chrome_options)

dfs = []
for k, v in grs.items():
    # get i page
    driver.get(base.format(place=v[1], gm_code=v[0]))
    sleep(3)
    
    # grab html
    generated_html = driver.page_source
    
    cells = BeautifulSoup(generated_html).findAll(
        'div',
        attrs={'class' : 'cell_content'}
    )
    
    weather = []
    for i, c in enumerate(cells):
        try:
            min_t = int(
                c
                .find('div', attrs={'class' : 'temp_min'})
                .find('span', attrs={'class' : 'unit_temperature_c'})
                .text
                .replace('\n', '')
                .replace(' ', '')
                .replace('−', '-')
            )
            max_t = int(
                c
                .find('div', attrs={'class' : 'temp_max'})
                .find('span', attrs={'class' : 'unit_temperature_c'})
                .text
                .replace('\n', '')
                .replace(' ', '')
                .replace('−', '-')
            )
            weather.append({
                'date': (datetime.now() + timedelta(days=i)).date(),
                'min_t': min_t,
                'max_t': max_t
            })
        except AttributeError:
            print(i, 'cell hasn\'t temp')
        
    df_weather = pd.DataFrame(weather)
    df_weather['place'] = v[1]
    df_weather['code'] = k
    dfs.append(df_weather.copy())

driver.quit()
    
df_future = pd.concat(dfs, sort=False)
df_future.to_csv('data/future.tsv', sep='\t', index=False)