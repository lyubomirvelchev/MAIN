from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch()
    context = browser.new_context()
    # Open new page
    page = context.new_page()
    # Go to https://example.com
    page.goto("https://example.com/")
    # Take screenshot
    page.screenshot(path="example.png")
    # Close page
    page.close()
    # ---------------------
    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)