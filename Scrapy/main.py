import requests
import newspaper
from newspaper import Article
from bs4 import BeautifulSoup

def get_url_html(url_str):
    html = requests.get(url_str)
    soup = BeautifulSoup(html.content, 'html.parser')
    a=9

def get_newspaper(url):
    hui = Article(url)
    hui.download()
    hui.parse()
    print('TITLE: ', hui.title)
    print(hui.url)
    print("META DESC: ", hui.meta_description)
    print("META KEYS: ", hui.meta_keywords)
    # print(hui.h1)
    soup = BeautifulSoup(hui.html, 'html.parser')
    print("H1: ", soup.find_all('h1')[0].get_text())
    print('TEXT: ', hui.text)
    print("")
    # print(soup.find_all('h2'))
    # print(soup.find_all('h3'))


if __name__ == '__main__':
    aa = r'https://www.finra.org/investors/learn-to-invest/types-investments/stocks/trading-vs-buy-and-hold'
    a = r'https://biomall.bg/kak-da-ovladeem-diariqta-burzo'
    b = r"https://towardsdatascience.com/web-scraping-news-articles-in-python-9dd605799558"
    c = r'https://moeto-zdrave.com/%D0%BF%D0%BE%D0%BB%D0%B5%D0%B7%D0%BD%D0%BE/kak-da-sprem-razstroystvoto'
    d = r'https://www.supichka.com/%D1%80%D0%B5%D1%86%D0%B5%D0%BF%D1%82%D0%B0/411/%D0%BF%D0%B8%D0%BB%D0%B5%D1%88%D0%BA%D0%B0-%D1%81%D1%83%D0%BF%D0%B0-%D0%BF%D0%BE-%D0%BA%D0%BB%D0%B0%D1%81%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%B0-%D1%80%D0%B5%D1%86%D0%B5%D0%BF%D1%82%D0%B0'
    e = r'https://matekitchen.com/recipes/pileshka-supa/'
    f = r'https://sofiaglobe.com/2022/07/14/bulgarias-pm-on-covid-19-no-closing-of-businesses-no-travel-restrictions/'
    g = r'https://www.healthline.com/health/vomiting-causes-treatment'
    h = r'https://www.businessinsider.com/how-to-screenshot-on-windows'
    i = r'https://www.dulyhealthandcare.com/health-topic/cant-stop-coughing-it-may-be-chronic-cough'
    j = r'https://www.health.harvard.edu/staying-healthy/that-nagging-cough'  # Fail
    k = r'https://truemoneysaver.com/money/budgeting/live-on-less/' # Fail
    l = r'https://medium.com/the-ascent/5-brutally-honest-reasons-life-is-worth-living-9f9d6a229857'  # Fail
    m = r'https://www.onthegotours.com/Holiday-ideas-for-August'


    l1 = r'https://www.rct.uk/collection/themes/trails/the-crown-jewels/the-cullinan-diamond'
    l2 = r"https://www.thecourtjeweller.com/2022/01/the-queens-cullinan-diamonds.html"
    l3 = r'https://www.history.com/this-day-in-history/worlds-largest-diamond-found'
    l4 = r'https://www.jewellermagazine.com/Article/537/Cullinan-1-9-World-Famous-Diamonds'
    l5 = r'http://www.cullinan-diamond.com/'

    b1 = r"https://backlinko.com/reverse-outreach"
    b2 = r"https://backlinko.com/video-marketing-guide"  # fail
    b3 = r"https://backlinko.com/introducing-content-marketing-hub-2-0"
    b4 = r"https://backlinko.com/evergreen-content-study"
    b5 = r"https://backlinko.com/email-marketing-guide"  # fail

    get_newspaper(a)
    get_newspaper(b)
    get_newspaper(c)
    get_newspaper(d)
    get_newspaper(e)