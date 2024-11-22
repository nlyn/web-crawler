# Standard Library
import logging
from urllib.parse import urljoin, urlparse

# Third-Party
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class Parser:
    def __init__(self, desired_link_domain):
        self.desired_link_domain = desired_link_domain

    def extract_links(self, html, base_url):
        """Extract all links from the given HTML content."""
        soup = BeautifulSoup(html, "html.parser")
        crawlable_urls = set()
        non_crawlable_urls = set()
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            full_url = urljoin(base_url, href)
            parsed_url = urlparse(full_url)
            if (
                parsed_url.netloc == self.desired_link_domain
            ):  # We only want to crawl links within the same domain
                crawlable_urls.add(full_url)
            else:
                non_crawlable_urls.add(full_url)
        return crawlable_urls, non_crawlable_urls
