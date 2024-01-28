from playwright.sync_api import sync_playwright
import time
from bs4 import BeautifulSoup

MAIN_URL = r'https://en.wikipedia.org'
MAIN_PAGE_URL = MAIN_URL + r'/wiki/Main_Page'
single_fact_selector_str = f'#mp-dyk > ul > li:nth-child'
thumbnail_img_selector_str = '#mp-dyk > div.dyk-img > div > span > a > img'
thumbnail_text_selector_str = '#mp-dyk > div.dyk-img > div > div'


def open_page(playwright, url):
    browser = playwright.chromium.launch()
    context = browser.new_context()
    page = context.new_page()
    page.goto(url)
    return page


def capture_section_featured_img_and_caption(page):
    img_locator = page.query_selector(thumbnail_img_selector_str)
    img_src = img_locator.get_attribute('src')
    text_locator = page.query_selector(thumbnail_text_selector_str)
    text = text_locator.inner_text()
    return img_src, text


def get_all_data(playwright, url):
    """
        This function scrapes the data from the Did you know page of Wikipedia, including links, and data from the
        popups that appear when hovering over the links.

        This function is very big and should be broken down into smaller functions
    """
    page = open_page(playwright, url)
    li_elements = page.query_selector_all('#mp-dyk > ul > li')
    data = {"featured_img": "", "featured_text": "", "facts": {}}
    featured_img, featured_text = capture_section_featured_img_and_caption(page)
    data['featured_img'] = featured_img
    data['featured_text'] = featured_text
    for idx in range(len(li_elements)):
        sub_data = {"fact_text": "", 'fact_links': []}
        locator_selector_str = single_fact_selector_str + f'({idx + 1})'
        single_fact_locator = page.query_selector(locator_selector_str)
        sub_data['fact_text'] = single_fact_locator.inner_text()
        link_elements = single_fact_locator.query_selector_all('a')
        for link_element in link_elements:
            fact_links = {}
            link_element.hover()
            time.sleep(2)  # should be async
            link_word = link_element._impl_obj._preview.split('>')[-2].split('<')[
                0]  # could not get the data any other way
            fact_links['link_word'] = link_word
            html = BeautifulSoup(page.content(), 'html.parser')
            try:
                link_href = html.select(single_fact_selector_str + f'({idx + 1})')[0].find('a', string=link_word)['href']
                link_page = link_href if link_href else ''
            except Exception as e:
                print(e)
                link_page = ''
            popup_img_tag = html.find_all(class_='mwe-popups-thumbnail')
            popup_text_tag = html.find_all(class_='mwe-popups-extract')
            fact_links['link_page'] = MAIN_URL + link_page
            fact_links['popup_img'] = popup_img_tag[0].get('src') if popup_img_tag else ''
            fact_links['popup_text'] = popup_text_tag[0].get_text(strip=True) if popup_text_tag else ''
            sub_data['fact_links'].append(fact_links)
        data['facts'][idx + 1] = sub_data
    page.close()
    return data


def main():
    with sync_playwright() as playwright:
        data = get_page_data(playwright, MAIN_PAGE_URL)
    return data


if __name__ == '__main__':
    import pprint
    data_dict = main()
    pprint.pprint(data_dict)
