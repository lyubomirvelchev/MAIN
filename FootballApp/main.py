from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import datetime as dt

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
CLASS_NAME = "css-d0m1xg-MatchWrapper ew7iiy61"
TIME_CLASS_NAME = "css-1t8tpw0-time"
LIVE_CLASS_NAME = "css-g3e0pm-score"
RESULT_CLASS_NAME = "css-1dfww3s-live"

today_date = dt.datetime.today()

print(today_date)

driver = webdriver.Chrome(options=chrome_options)

driver.get('https://www.fotmob.com/?show=all&filter=&date=20230320')

html = driver.page_source
matches = html.split(CLASS_NAME)
counter = 0
for match in matches:
    # print(match)
    counter += 1
    print(counter)

driver.quit()

