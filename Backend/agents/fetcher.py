from playwright.sync_api import sync_playwright

def fetch_html(url):
    """
    Fetch HTML content of the given URL using Playwright
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)  # wait max 60s
        html = page.content()
        browser.close()
        return html
