import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:96.0) Gecko/20100101 Firefox/96.0'}
HOST = 'https://www.helpguide.org'
PAGE = 'articles/sleep/getting-better-sleep.htm'
with requests.Session() as session:
    (r := session.get(HOST, headers=headers)).raise_for_status()
    (r := session.get(f'{HOST}/{PAGE}', headers=headers)).raise_for_status()
    soup = BeautifulSoup(r.content, 'html.parser')
    a = 9
    print(soup.find('h2'))
