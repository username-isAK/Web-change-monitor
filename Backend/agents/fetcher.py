from playwright.sync_api import sync_playwright

def fetch_html(url):
    """
    Fetch HTML content of the given URL using Playwright
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=60000, wait_until="domcontentloaded")
            html = page.content()
            browser.close()
            return html
    except Exception as e:
        raise Exception(f"Failed to fetch {url}: {str(e)}")