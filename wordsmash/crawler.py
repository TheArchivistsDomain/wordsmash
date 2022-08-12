from re import compile
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from requests import get


class Crawler:
    def __init__(self, root_url: str, limit: int = 20):
        self.root_url = root_url
        self.urls_to_visit = [root_url]
        self.limit = limit

        self.visited_urls = []
        self.emails = []

        self.ignore_types = [
            ".JPEG",
            ".JPG",
            ".BMP",
            ".PNG",
            ".GIF",
            ".TIFF",
            ".PDF",
            ".JS",
            ".CSS",
        ]

    def crawl(self, url: str) -> None:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/101.0"
        }
        html = get(url, headers=headers, verify=False).text

        for url in self.get_linked_urls(url, html):
            if url:
                if url.startswith(self.root_url):
                    if not url.endswith("/"):
                        url = url + "/"

                    if (
                        url.strip() not in self.visited_urls
                        and url not in self.urls_to_visit
                        and not any(
                            ext in url.upper() for ext in self.ignore_types
                        )
                    ):
                        self.urls_to_visit.append(url)

    def get_linked_urls(self, url: str, html: str) -> None:
        soup = BeautifulSoup(html, "lxml")
        email = compile(
            r"([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+){0,}"
        )
        self.emails.extend([x for x in soup.strings if email.search(x).group()])

        for link in soup.find_all("a"):
            path = link.get("href")
            if path and path.startswith("/"):
                path = urljoin(url, path)
            yield path

    def run(self) -> list:
        counter = 1
        while self.urls_to_visit:
            url = self.urls_to_visit.pop(0).strip()
            if not url.endswith("/"):
                url = url + "/"

            if (
                url.startswith(self.root_url)
                and url.strip() not in self.visited_urls
                and self.limit >= counter
            ):
                try:
                    self.crawl(url)
                except Exception as e:
                    print(f"Failed to crawl {url}: {e.message}")
                finally:
                    self.visited_urls.append(url.strip())
                    counter += 1

        self.emails = list(dict.fromkeys(self.emails))
        return self.emails
