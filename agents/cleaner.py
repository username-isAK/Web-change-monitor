# agents/cleaner.py
from bs4 import BeautifulSoup

def clean_html(html):
    """
    Clean raw HTML using BeautifulSoup and extract readable text
    """
    soup = BeautifulSoup(html, "lxml")

    # remove unwanted tags
    for tag in soup(["script", "style", "header", "footer", "nav"]):
        tag.decompose()

    # extract text
    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    clean_text = "\n".join(lines)
    return clean_text
