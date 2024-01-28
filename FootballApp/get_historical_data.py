from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import datetime as dt
import time
import re
from bs4 import BeautifulSoup
import pprint

from thirty_days_links import HUI

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')

ALL_LINKS = {}
END_RESULT = {}
CLASS_NAME = "css-d0m1xg-MatchWrapper ew7iiy61"
TIME_CLASS_NAME = "css-1t8tpw0-time"
SCORE_CLASS_NAME = "css-g3e0pm-score"
END_SCORE_CLASS_NAME = "</span>"
RESULT_CLASS_NAME = "css-1dfww3s-live"
PLAYER_MINUTE_SCORED = 'css-1tkqwax-EventTime e3q4wbq0'

today_date = dt.datetime.today()
driver = webdriver.Chrome(options=chrome_options)


def get_historical_data_for_single_day(date, counter=4):
    if counter == 0:
        return []
    if counter % 2 == 0:
        URL = 'https://www.fotmob.com/?show=all&filter=&date=' + date + '&q='
    else:
        URL = 'https://www.fotmob.com/?show=all&filter=&date=' + date
    driver.get(URL)
    links = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    matches = soup.find_all('a', class_=CLASS_NAME)
    for match in matches:
        try:
            score = match.find('span', class_=SCORE_CLASS_NAME).text
            overall_score = int(score[0]) + int(score[-1])
            if overall_score >= 3:
                links.append(match['href'])
        except AttributeError:
            pass

    if len(matches) == 0:
        return get_historical_data_for_single_day(date, counter - 1)

    print("Done with " + date)
    print('Counter: ' + str(counter))
    print("Number of matches: " + str(len(matches)))
    print("Number of links: " + str(len(links)))
    print("-------------------------------------------------------------")
    return links


def get_scoring_minutes(url, counter=4):
    time.sleep(3.5)
    if counter == 0:
        return []
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    try:
        scores = soup.find_all('span', class_=PLAYER_MINUTE_SCORED)
        if len(scores) == 0:
            return get_scoring_minutes(url, counter - 1)
        else:
            numbers = []
            for score in scores:
                numbers.append(re.findall(r'\d+', score.text))
            numbers_int = sorted([int(x) for sublist in numbers for x in sublist])
            print("Minutes:", numbers_int)
            print("-------------------------------------------------------------")
            return numbers_int
    except Exception as e:
        print(e)
        print(url)


def get_historical_data_for_number_of_days_ago(days):
    for i in range(days):
        date_before = today_date - dt.timedelta(days=i + 1)
        date_str = date_before.strftime("%Y%m%d")
        links = get_historical_data_for_single_day(date_str)
        ALL_LINKS[date_str] = links


# get_historical_data_for_number_of_days_ago(30)
ALL_LINKS = HUI
# pprint.pprint(ALL_LINKS)

for key, single_day_links in ALL_LINKS.items():
    time.sleep(3.5)
    for single_link in single_day_links:
        url = 'https://www.fotmob.com' + single_link
        scores = get_scoring_minutes(url)
        first_half_goals = 0
        if scores is None:
            a = 0
        for x in scores:
            if x <= 45:
                first_half_goals += 1
        second_half_goals = len(scores) - first_half_goals
        if first_half_goals > 2:
            if first_half_goals not in END_RESULT.keys():
                END_RESULT[first_half_goals] = [second_half_goals]
            else:
                END_RESULT[first_half_goals].append(second_half_goals)

            if second_half_goals == 0:
                print('Lose money at ' + key + ' on ' + url)
                print("-------------------------------------------------------------")
    print("After " + key + " we have: ", END_RESULT)
    print("-------------------------------------------------------------")

pprint.pprint(END_RESULT)

driver.quit()
