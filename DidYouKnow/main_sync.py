import time
import pprint
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

MAIN_URL = r'https://en.wikipedia.org'
MAIN_PAGE_URL = MAIN_URL + r'/wiki/Main_Page'
popup_img_selector_str = 'mwe-popups-thumbnail'
popup_text_selector_str = 'mwe-popups-extract'
li_elements_selector_str = '#mp-dyk > ul > li'
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


def get_single_fact_data(page, idx):
    sub_data = {"fact_text": "", 'fact_links': []}
    locator_selector_str = single_fact_selector_str + f'({idx + 1})'
    single_fact_locator = page.query_selector(locator_selector_str)
    sub_data['fact_text'] = single_fact_locator.inner_text()
    link_elements = single_fact_locator.query_selector_all('a')
    for link_element in link_elements:
        link_element.hover()
        link_data = {}
        time.sleep(2)  # should be async
        page.pause()
        link_word = link_element._impl_obj._preview.split('>')[-2].split('<')[0]  # could not get the data any other way
        link_page = MAIN_URL + link_element._impl_obj._preview.split("href=\"")[-1].split("\"")[0]
        link_data['link_word'] = link_word
        link_data['link_page'] = link_page
        html = BeautifulSoup(page.content(), 'html.parser')
        popup_img_tag = html.find_all(class_=thumbnail_img_selector_str)
        link_data['popup_img'] = popup_img_tag[0].get('src') if popup_img_tag else ''
        popup_text_tag = html.find_all(class_=thumbnail_text_selector_str)
        link_data['popup_text'] = popup_text_tag[0].get_text(strip=True) if popup_text_tag else ''
        sub_data['fact_links'].append(link_data)
    return sub_data


def get_page_data(playwright, url):
    page = open_page(playwright, url)
    data = {"featured_img": "", "featured_text": "", "facts": {}}
    featured_img, featured_text = capture_section_featured_img_and_caption(page)
    data['featured_img'] = featured_img
    data['featured_text'] = featured_text
    li_elements = page.query_selector_all(li_elements_selector_str)
    for idx in range(len(li_elements)):
        data['facts'][idx + 1] = get_single_fact_data(page, idx)
    page.close()
    return data


def main():
    with sync_playwright() as playwright:
        scrape_data = get_page_data(playwright, MAIN_PAGE_URL)
    return scrape_data


if __name__ == '__main__':
    main_data = main()
    pprint.pprint(main_data)
