from src.rss import fetch_rss


class DummyResponse:
    def __init__(self, content: bytes):
        self.content = content
        self.headers = {"content-type": "application/rss+xml; charset=utf-8"}

    def raise_for_status(self):
        return None


def test_fetch_rss_parses_response_content(monkeypatch):
    xml = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Demo Feed</title>
    <item>
      <title>Hello</title>
      <link>https://example.com/hello</link>
      <pubDate>Tue, 10 Mar 2026 10:00:00 GMT</pubDate>
      <description>World</description>
    </item>
  </channel>
</rss>
"""

    monkeypatch.setattr("src.rss.requests.get", lambda *args, **kwargs: DummyResponse(xml))

    entries = fetch_rss("https://example.com/feed.xml")

    assert len(entries) == 1
    assert entries[0]["title"] == "Hello"
    assert entries[0]["link"] == "https://example.com/hello"
