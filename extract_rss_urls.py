#!/usr/bin/env python3
"""解析 OPML 文件提取 RSS feeds"""

import xml.etree.ElementTree as ET
from typing import List

def parse_opml(opml_file: str) -> List[dict]:
    tree = ET.parse(opml_file)
    root = tree.getroot()

    feeds = []

    for outline in root.findall('.//outline'):
        xml_url = outline.get('xmlUrl')
        if xml_url:
            feeds.append({
                'title': outline.get('title', outline.get('text', 'Unknown')),
                'url': xml_url,
                'html_url': outline.get('htmlUrl', ''),
            })

    return feeds

if __name__ == "__main__":
    feeds = parse_opml("/Users/a1-6/Downloads/新闻抓取脚本/Feeds.opml")

    print(f"找到 {len(feeds)} 个 RSS feeds:\n")

    urls_only = []
    for feed in feeds:
        urls_only.append(feed['url'])
        print(f"- {feed['title']}")
        print(f"  URL: {feed['url']}\n")

    with open("extracted_urls.py", "w") as f:
        f.write("RSS_URLS = [\n")
        for url in urls_only:
            f.write(f'    "{url}",\n')
        f.write("]\n")

    print(f"\n✅ 已提取 {len(urls_only)} 个 RSS URLs")
    print(f"✅ 已保存到 extracted_urls.py")
