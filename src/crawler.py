# Standard Library
import asyncio
import logging
from collections import deque
from urllib.parse import urlparse

# Third-Party
import aiohttp
import typer

# Local Folder
from .fetcher import Fetcher
from .parser import Parser

logger = logging.getLogger(__name__)


class Crawler:
    def __init__(
        self,
        start_url,
        max_concurrent_tasks,
        rate_limit_per_task=0,
        max_retries=3,
        retry_delay=1,
    ):
        self.visited_urls = set()
        self.url_queue = deque([start_url])
        self.max_concurrent_tasks = max_concurrent_tasks
        self.rate_limit_per_task = rate_limit_per_task
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.fetcher = Fetcher(max_retries, retry_delay)
        self.parser = Parser(desired_link_domain=urlparse(start_url).netloc)

    async def fetch_and_crawl(self, session, url, semaphore):
        """Fetch the URL and crawl for new links with retry mechanism."""
        async with semaphore:
            try:
                html = await self.fetcher.fetch_with_retries(session, url)

                if html:

                    crawlable_urls, non_crawlable_urls = self.parser.extract_links(
                        html, url
                    )
                    typer.echo(
                        typer.style(f"Visited: {url}", fg=typer.colors.GREEN, bold=True)
                    )
                    typer.echo("Crawlable links found:")

                    for crawlable_url in crawlable_urls:
                        typer.echo(
                            typer.style(f"  {crawlable_url}", fg=typer.colors.CYAN)
                        )
                        if (
                            crawlable_url not in self.visited_urls
                            and crawlable_url not in self.url_queue
                        ):
                            self.url_queue.append(crawlable_url)

                    typer.echo("Non-crawlable links:")
                    for non_crawlable_url in non_crawlable_urls:
                        typer.echo(
                            typer.style(
                                f"  {non_crawlable_url}", fg=typer.colors.YELLOW
                            )
                        )

                # Sleep after each fetch to respect rate limit per task
                if self.rate_limit_per_task:
                    await asyncio.sleep(self.rate_limit_per_task)

            except Exception as e:
                logger.error(
                    f"Unexpected error during fetch_and_crawl: {e}",
                    exc_info=True,
                )

    async def crawl(self):
        """Crawl starting from the initial URL."""
        semaphore = asyncio.Semaphore(self.max_concurrent_tasks)
        async with aiohttp.ClientSession() as session:
            try:
                while self.url_queue:
                    tasks = []
                    for _ in range(min(len(self.url_queue), self.max_concurrent_tasks)):
                        if not self.url_queue:
                            break
                        current_url = self.url_queue.popleft()
                        if current_url not in self.visited_urls:
                            self.visited_urls.add(current_url)
                            tasks.append(
                                self.fetch_and_crawl(session, current_url, semaphore)
                            )
                    if tasks:
                        await asyncio.gather(*tasks)
            except asyncio.CancelledError:
                logger.info("Crawl cancelled")
            except Exception as e:
                logger.error(f"Unexpected error during crawl: {e}", exc_info=True)
