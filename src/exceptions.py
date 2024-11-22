class ClientErrorException(Exception):
    """Exception raised for client errors (4xx)."""

    pass


class RetryableErrorException(Exception):
    """Exception raised for retryable errors (e.g., network issues, server errors)."""

    pass
