# Standard Library
from unittest.mock import AsyncMock, MagicMock, Mock

# Third-Party
import aiohttp
import pytest

# First-Party
from src.exceptions import ClientErrorException, RetryableErrorException
from src.fetcher import Fetcher


@pytest.fixture
def fetcher():
    return Fetcher(
        retry_delay=0.01,  # low so that tests run faster
        max_retries=3,
    )


@pytest.fixture
def mock_session():
    session = MagicMock()
    mock_get = AsyncMock()
    mock_get.__aexit__ = AsyncMock()
    session.get.return_value = mock_get
    return session


@pytest.fixture
def mock_response():
    response = AsyncMock()
    response.headers = MagicMock()
    response.headers.get = MagicMock()
    return response


def setup_mock_response(mock_session, mock_response):
    async def mock_aenter(self):
        return mock_response

    async def mock_aexit(self, exc_type, exc, tb):
        pass

    mock_session.get.return_value.__aenter__ = mock_aenter
    mock_session.get.return_value.__aexit__ = mock_aexit


@pytest.mark.asyncio
async def test_fetch_success(fetcher, mock_session, mock_response):
    url = "http://example.com"
    mock_response.status = 200
    mock_response.headers.get.return_value = "text/html"
    mock_response.text.return_value = "<html></html>"
    setup_mock_response(mock_session, mock_response)

    response = await fetcher.fetch_with_retries(mock_session, url)
    assert response == "<html></html>"
    mock_session.get.assert_called_once_with(url, timeout=10, raise_for_status=True)


@pytest.mark.asyncio
async def test_fetch_non_html(fetcher, mock_session, mock_response):
    url = "http://example.com"
    mock_response.status = 200
    mock_response.headers.get.return_value = "application/json"
    mock_response.text.return_value = "{}"
    setup_mock_response(mock_session, mock_response)

    response = await fetcher.fetch_with_retries(mock_session, url)
    assert response is None
    mock_session.get.assert_called_once_with(url, timeout=10, raise_for_status=True)


@pytest.mark.asyncio
async def test_fetch_404(fetcher, mock_session):
    url = "http://example.com"
    mock_session.get = Mock(
        side_effect=aiohttp.ClientResponseError(
            request_info=None,
            history=None,
            status=404,
            message="Not Found",
            headers=None,
        )
    )

    response = await fetcher.fetch_with_retries(mock_session, url)
    assert response is None

    mock_session.get.assert_called_once_with(url, timeout=10, raise_for_status=True)


@pytest.mark.asyncio
async def test_fetch_500(fetcher, mock_session):
    url = "http://example.com"
    mock_session.get = Mock(
        side_effect=aiohttp.ClientResponseError(
            request_info=None,
            history=None,
            status=500,
            message="Internal Server Error",
            headers=None,
        )
    )

    response = await fetcher.fetch_with_retries(mock_session, url)
    assert response is None

    assert mock_session.get.call_count == fetcher.max_retries + 1
