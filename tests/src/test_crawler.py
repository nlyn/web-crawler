# Standard Library
import asyncio
import unittest
from collections import deque
from unittest.mock import AsyncMock, Mock, patch

# Third-Party
import pytest
from aiohttp import ClientSession

# First-Party
from src.crawler import Crawler


@pytest.fixture
def crawler():
    start_url = "https://example.com"
    max_concurrent_tasks = 5
    rate_limit_per_task = 0.1
    max_retries = 3
    retry_delay = 0.1
    return Crawler(
        start_url, max_concurrent_tasks, rate_limit_per_task, max_retries, retry_delay
    )


@pytest.mark.asyncio
async def test_crawl(crawler):
    crawler.url_queue = deque(["https://httpbin.org/html"])

    mock_fetch = AsyncMock(
        return_value="<html><a href='https://httpbin.org/page'>Page</a></html>"
    )
    crawler.fetcher.fetch_with_retries = mock_fetch

    mock_extract_links = Mock(return_value=(["https://httpbin.org/page"], []))
    crawler.parser.extract_links = mock_extract_links

    async with ClientSession() as session:
        await crawler.crawl()

    assert "https://httpbin.org/html" in crawler.visited_urls
    assert "https://httpbin.org/page" in crawler.visited_urls

    assert mock_extract_links.call_count == 2
    mock_extract_links.assert_has_calls(
        [
            unittest.mock.call(
                "<html><a href='https://httpbin.org/page'>Page</a></html>",
                "https://httpbin.org/html",
            ),
            unittest.mock.call(
                "<html><a href='https://httpbin.org/page'>Page</a></html>",
                "https://httpbin.org/page",
            ),
        ]
    )

    assert mock_fetch.call_count == 2


@pytest.mark.asyncio
async def test_visit_all_urls(crawler):
    crawler.max_concurrent_tasks = 2
    crawler.url_queue = deque([f"https://example.com/page{i}" for i in range(20)])

    async def mock_fetch_and_crawl(*args, **kwargs):
        await asyncio.sleep(0.1)
        crawler.visited_urls.add(args[1])

    with patch.object(crawler, "fetch_and_crawl", side_effect=mock_fetch_and_crawl):
        await crawler.crawl()

    assert len(crawler.visited_urls) == 20
    assert crawler.max_concurrent_tasks == 2


@pytest.mark.asyncio
async def test_dont_revisit_urls(crawler):
    # ad the same URL twice
    crawler.url_queue = deque(
        ["https://example.com/page1", "https://example.com/page1"]
    )

    async def mock_fetch_and_crawl(*args, **kwargs):
        crawler.visited_urls.add(args[1])

    with patch.object(crawler, "fetch_and_crawl", side_effect=mock_fetch_and_crawl):
        await crawler.crawl()

    assert len(crawler.visited_urls) == 1
    assert "https://example.com/page1" in crawler.visited_urls


@pytest.mark.asyncio
async def test_rate_limit_per_task(crawler):
    crawler.rate_limit_per_task = 0.01  # something small so the test runs quickly
    crawler.url_queue = deque([f"https://example.com/page{i}" for i in range(3)])

    mock_fetch = AsyncMock(
        return_value="<html><a href='https://httpbin.org/page'>Page</a></html>"
    )
    crawler.fetcher.fetch_with_retries = mock_fetch

    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        await crawler.crawl()
        assert mock_sleep.call_count == 3
        mock_sleep.assert_any_call(0.01)
