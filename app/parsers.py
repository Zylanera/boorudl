from urllib.parse import urljoin
from bs4 import BeautifulSoup

def extract_image_url(page_url, soup: BeautifulSoup):
    sec = soup.select_one("section.image-container, .image-container")
    if sec:
        for a in ("data-file-url", "data-large-file-url"):
            if sec.get(a):
                return urljoin(page_url, sec[a])

    og = soup.find("meta", property="og:image")
    if og and og.get("content"):
        return urljoin(page_url, og["content"])
    return None
