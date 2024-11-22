# Standard Library
import asyncio
import logging

# Third-Party
import aiohttp

# Local Folder
from .exceptions import ClientErrorException, RetryableErrorException

logger = logging.getLogger(__name__)


class Fetcher:
    def __init__(self, max_retries=3, retry_delay=1):
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    async def fetch(self, session, url):
        """Fetch the content of the given URL with granular error handling."""
        try:
            async with session.get(url, timeout=10, raise_for_status=True) as response:
                if "text/html" in response.headers.get("Content-Type", ""):
                    return await response.text()
                else:
                    logger.warning(f"Skipping non-HTML content at {url}")
                    return None
        except aiohttp.ClientResponseError as e:
            if 400 <= e.status < 500:
                logger.error(f"Client error {e.status} fetching {url}: {e.message}")
                raise ClientErrorException(f"Client error {e.status} fetching {url}")
            else:
                logger.error(f"Server error {e.status} fetching {url}: {e.message}")
                raise RetryableErrorException(f"Server error {e.status} fetching {url}")
        except (
            aiohttp.ClientConnectorError,
            asyncio.TimeoutError,
            aiohttp.ClientError,
        ) as e:
            logger.error(f"Error fetching {url}: {e}")
            raise RetryableErrorException(f"Error fetching {url}")
        except Exception as e:
            logger.error(f"Unexpected error fetching {url}: {e}")
            raise RetryableErrorException(f"Unexpected error fetching {url}")

    async def fetch_with_retries(self, session, url):
        """Fetch the URL with retry mechanism."""
        retries = 0
        while retries <= self.max_retries:
            try:
                return await self.fetch(session, url)
            except ClientErrorException:
                return None
            except RetryableErrorException as e:
                retries += 1
                if retries > self.max_retries:
                    logger.warning(f"Max retries reached for {url}, giving up.")
                    return None
                logger.warning(
                    f"Retryable error encountered for {url}: {e}. Retrying ({retries}/{self.max_retries})..."
                )
                await asyncio.sleep(self.retry_delay)
            except Exception as e:
                logger.error(f"Unexpected error during fetch: {e}", exc_info=True)
                return None
