# Web Crawler

## Design

The crawler is designed to be fault-tolerant, efficient, and configurable. It consists of the following components:

1. **CLI Interface**: A simple command-line interface for users to start the crawler with a specified URL and configuration options.
2. **Crawler Class**: Manages the crawling process, including URL queuing, visiting pages, and ensuring concurrency and rate limiting.
3. **Fetcher Class**: Handles the fetching of web pages with retry logic.
4. **Parser Class**: Parses HTML content to extract links.

### Design Decisions

- **Concurrency**: Utilized `asyncio` for managing concurrent tasks, which allows for crawling multiple pages simultaneously without blocking.
- **Error Handling**: Implemented retry logic and error handling to ensure the crawler can recover from transient network issues.
- **Rate Limiting**: Implemented delay between requests inside of each asynchronous task to prevent overwhelming the server.
- **HTML Parsing**: Used `BeautifulSoup` for efficient HTML parsing and link extraction.

### Trade-offs

- **Rate Limiting**: A fixed delay is used for simplicity. A more sophisticated approach could be to use a dynamic rate limiter so that the crawler can adapt to the server's response time.
- **Exponential Backoff**: The retry logic uses a fixed delay between retries instead of exponential backoff. Exponential backoff could be more efficient in some cases.
- **Breadth-First vs. Depth-First**: The current queue implementation processes URLs in a depth-first manner. Depending on the use case, a breadth-first approach might be more appropriate. This would likely be slower but would ensure that all pages at a given depth are processed before moving to the next depth.

## Dependencies

The program uses the following dependencies:

- **aiohttp** for making asynchronous HTTP requests
- **BeautifulSoup** for parsing HTML
- **asyncio** for managing asynchronous tasks
- **typer** for creating the CLI interface

## Installation

This project uses Poetry for dependency management. To install Poetry, follow the instructions on the [official website](https://python-poetry.org/docs/#installation).

Once Poetry is installed, you can set up the project environment and install the dependencies by running:

```bash
poetry install
```

## Usage

You can run the crawler from the command line using the provided CLI interface. Here’s how to get started:

```bash
poetry run python main.py --url https://en.wikipedia.org --max-concurrent-tasks 5 --rate-limit 1
```

### Command-Line Arguments:

- `--url`: The starting URL for the crawler (required)
- `--max-concurrent-tasks`: The maximum number of concurrent tasks (default: 5)
- `--rate-limit`: The delay between requests in seconds (default: 1)
- `--max-retries`: The maximum number of retries for failed requests (default: 3)
- `--retry-delay`: The delay between retries in seconds (default: 1)
- `--help`: Show the help message

### Testing

You can run the test suite using the following command:

```bash
poetry run pytest
```

The tests cover the core functionality of the crawler, including URL extraction, fetching, and parsing.

## Future Improvements

Here are some potential improvements that could be made to the crawler:

- **User-Agent Rotation**: Rotate user agents to prevent being blocked by servers that detect and block crawlers.
- **Proxy Support**: Add support for rotating proxies to avoid IP-based blocking.
- **Persistent Storage**: Store visited URLs and links in a database for resuming crawls and analyzing results.
- **Depth Limitation**: The current implementation does not limit the depth of crawling. Adding a depth limit could prevent excessively deep crawls on large sites.
- **Robots.txt Parsing**: Implement parsing of `robots.txt` files to respect crawling rules specified by the website.
- **Logging**: Add more detailed logging to track the crawling process and errors.
