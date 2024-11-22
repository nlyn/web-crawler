import pytest
from typer.testing import CliRunner
from unittest.mock import patch, AsyncMock
import main

runner = CliRunner()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "url, max_concurrent_tasks, rate_limit, max_retries, retry_delay",
    [
        ("http://example.com", 5, 1, 3, 1),
        ("http://example.com", 10, 2, 5, 2),
        ("http://example.com", 1, 0, 1, 0.5),
    ],
)
async def test_run_crawler(
    url, max_concurrent_tasks, rate_limit, max_retries, retry_delay
):
    with patch("main.Crawler") as MockCrawler:
        mock_crawler_instance = MockCrawler.return_value
        mock_crawler_instance.crawl = AsyncMock()

        await main.run_crawler(
            url, max_concurrent_tasks, rate_limit, max_retries, retry_delay
        )

        MockCrawler.assert_called_once_with(
            start_url=url,
            max_concurrent_tasks=max_concurrent_tasks,
            rate_limit_per_task=rate_limit,
            max_retries=max_retries,
            retry_delay=retry_delay,
        )
        mock_crawler_instance.crawl.assert_called_once()


@pytest.mark.parametrize(
    "args, expected_url, expected_max_concurrent_tasks, expected_rate_limit, expected_max_retries, expected_retry_delay",
    [
        (
            [
                "--url",
                "http://example.com",
                "--max-concurrent-tasks",
                "5",
                "--rate-limit",
                "1",
                "--max-retries",
                "3",
                "--retry-delay",
                "1",
            ],
            "http://example.com",
            5,
            1,
            3,
            1,
        ),
        (
            [
                "--url",
                "http://example.com",
                "--max-concurrent-tasks",
                "10",
                "--rate-limit",
                "2",
                "--max-retries",
                "5",
                "--retry-delay",
                "2",
            ],
            "http://example.com",
            10,
            2,
            5,
            2,
        ),
        (
            [
                "--url",
                "http://example.com",
                "--max-concurrent-tasks",
                "1",
                "--rate-limit",
                "0",
                "--max-retries",
                "1",
                "--retry-delay",
                "0.5",
            ],
            "http://example.com",
            1,
            0,
            1,
            0.5,
        ),
    ],
)
def test_main(
    args,
    expected_url,
    expected_max_concurrent_tasks,
    expected_rate_limit,
    expected_max_retries,
    expected_retry_delay,
):
    with patch("main.run_crawler") as mock_run:
        result = runner.invoke(main.app, args)

        assert result.exit_code == 0
        mock_run.assert_called_once_with(
            expected_url,
            expected_max_concurrent_tasks,
            expected_rate_limit,
            expected_max_retries,
            expected_retry_delay,
        )
