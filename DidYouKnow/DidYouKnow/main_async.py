from playwright.async_api import async_playwright
import asyncio
from bs4 import BeautifulSoup

MAIN_URL = r'https://en.wikipedia.org'
MAIN_PAGE_URL = MAIN_URL + r'/wiki/Main_Page'
popup_container_selector_str = '.mwe-popups-container'
popup_img_selector_str = 'mwe-popups-thumbnail'
popup_text_selector_str = 'mwe-popups-extract'
li_elements_selector_str = '#mp-dyk > ul > li'
single_fact_selector_str = f'#mp-dyk > ul > li:nth-child'
thumbnail_img_selector_str = '#mp-dyk > div.dyk-img > div > span > a > img'
thumbnail_text_selector_str = '#mp-dyk > div.dyk-img > div > div'


async def open_page(playwright, url):
    browser = await playwright.chromium.launch()
    context = await browser.new_context()
    page = await context.new_page()
    await page.goto(url)
    return page


async def capture_section_featured_img_and_caption(page):
    img_locator = await page.query_selector(thumbnail_img_selector_str)
    img_src = await img_locator.get_attribute('src')
    text_locator = await page.query_selector(thumbnail_text_selector_str)
    text = await text_locator.inner_text()
    return img_src, text


async def process_single_fact(idx, page):
    sub_data = {"fact_text": "", 'fact_links': []}
    locator_selector_str = single_fact_selector_str + f'({idx + 1})'
    single_fact_locator = await page.query_selector(locator_selector_str)
    sub_data['fact_text'] = await single_fact_locator.inner_text()
    link_elements = await single_fact_locator.query_selector_all('a')
    for link_element in link_elements:
        link_data = {}
        await link_element.hover()
        await page.wait_for_selector(popup_container_selector_str, state="visible")
        link_word = link_element._impl_obj._preview.split('>')[-2].split('<')[0]  # could not get the data any other way
        link_page = MAIN_URL + link_element._impl_obj._preview.split("href=\"")[-1].split("\"")[0]
        link_data['link_word'] = link_word
        link_data['link_page'] = link_page
        html = BeautifulSoup(await page.content(), 'html.parser')
        popup_img_tag = html.find_all(class_=popup_img_selector_str)
        link_data['popup_img'] = popup_img_tag[0].get('src') if popup_img_tag else ''
        popup_text_tag = html.find_all(class_=popup_text_selector_str)
        link_data['popup_text'] = popup_text_tag[0].get_text() if popup_text_tag else ''
        sub_data['fact_links'].append(link_data)
    return idx + 1, sub_data


async def get_page_data(playwright, url):
    page = await open_page(playwright, url)
    li_elements = await page.query_selector_all(li_elements_selector_str)
    data = {"featured_img": "", "featured_text": "", "facts": {}}
    featured_img, featured_text = await capture_section_featured_img_and_caption(page)
    data['featured_img'] = featured_img
    data['featured_text'] = featured_text
    tasks = [process_single_fact(idx, page) for idx in range(len(li_elements))]
    facts = await asyncio.gather(*tasks)
    for idx, fact_data in facts:
        data['facts'][idx] = fact_data
    await page.close()
    return data


async def main():
    async with async_playwright() as playwright:
        data = await get_page_data(playwright, MAIN_PAGE_URL)
    return data


if __name__ == '__main__':
    import pprint
    hui = asyncio.run(main())
    pprint.pprint(hui)

