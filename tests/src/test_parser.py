# First-Party
from src.parser import Parser


def test_extract_links():
    parser = Parser(desired_link_domain="example.com")
    html = """
    <html>
        <body>
            <a href="http://example.com/page1">Page 1</a>
            <a href="http://example.com/page2">Page 2</a>
            <a href="http://external.com/page">External Page</a>
        </body>
    </html>
    """
    base_url = "http://example.com"

    links, unwanted_links = parser.extract_links(html, base_url)
    assert "http://example.com/page1" in links
    assert "http://example.com/page2" in links
    assert "http://external.com/page" not in links
    assert "http://external.com/page" in unwanted_links


def test_extract_relative_links():
    parser = Parser(desired_link_domain="example.com")
    html = """
    <html>
        <body>
            <a href="/page1">Page 1</a>
            <a href="/page2">Page 2</a>
        </body>
    </html>
    """
    base_url = "http://example.com"

    links, unwanted_links = parser.extract_links(html, base_url)
    assert "http://example.com/page1" in links
    assert "http://example.com/page2" in links
