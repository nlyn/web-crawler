# Standard Library
import asyncio
import logging

# Third-Party
import typer

# First-Party
from src.crawler import Crawler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = typer.Typer()


async def run_crawler(url, max_concurrent_tasks, rate_limit, max_retries, retry_delay):
    logger.info(
        f"Starting crawl of {url} with a max of {max_concurrent_tasks} concurrent tasks, "
        f"a rate limit of {rate_limit} per task, a max of {max_retries} retries, and a {retry_delay} second retry delay"
    )
    crawler = Crawler(
        start_url=url,
        max_concurrent_tasks=max_concurrent_tasks,
        rate_limit_per_task=rate_limit,
        max_retries=max_retries,
        retry_delay=retry_delay,
    )
    await crawler.crawl()


@app.command()
def main(
    url: str = typer.Option(..., "--url", help="The URL to start crawling"),
    max_concurrent_tasks: int = typer.Option(
        5,
        "--max-concurrent-tasks",
        help="The maximum number of concurrent tasks",
    ),
    rate_limit: float = typer.Option(
        0, "--rate-limit", help="The rate limit per task in seconds"
    ),
    max_retries: int = typer.Option(
        3, "--max-retries", help="The maximum number of retries"
    ),
    retry_delay: float = typer.Option(
        1, "--retry-delay", help="The delay between retries"
    ),
):
    asyncio.run(
        run_crawler(url, max_concurrent_tasks, rate_limit, max_retries, retry_delay)
    )


if __name__ == "__main__":
    app()
