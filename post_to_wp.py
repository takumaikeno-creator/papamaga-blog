#!/usr/bin/env python3
import os
import requests
import markdown
import re
import sys
from pathlib import Path

WP_URL = "https://www.papa-maga.online"
USER = os.environ.get("WP_USER", "")
APP_PASS = os.environ.get("WP_APP_PASS", "")
AUTH = (USER, APP_PASS)

MD_EXT = ["tables", "fenced_code", "nl2br", "sane_lists"]

def md_to_html(text):
    return markdown.markdown(text, extensions=MD_EXT)

def extract_title(md_text):
    for line in md_text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return "無題"

def post(endpoint, payload):
    url = f"{WP_URL}/?rest_route=/wp/v2/{endpoint}"
    r = requests.post(url, auth=AUTH, json=payload)
    return r

def create_post(md_path, post_type="posts", status="publish"):
    text = Path(md_path).read_text(encoding="utf-8")
    title = extract_title(text)
    body = re.sub(r"^# .+\n", "", text, count=1).strip()
    html = md_to_html(body)
    payload = {"title": title, "content": html, "status": status}
    r = post(post_type, payload)
    if r.status_code in (200, 201):
        data = r.json()
        print(f"✅ 投稿成功: {title}")
        print(f"   URL: {data.get('link', '')}")
        print(f"   ID : {data.get('id', '')}")
        return data
    else:
        print(f"❌ 投稿失敗: {title}  ({r.status_code})")
        print(f"   {r.text[:300]}")
        return None

if __name__ == "__main__":
    base = Path("/home/user/papamaga-blog/articles")

    print("=== メイン記事を投稿（post）===")
    create_post(base / "robot-vacuum-for-busy-dads.md", post_type="posts")

    print("\n=== プライバシーポリシーを投稿（page）===")
    create_post(base / "privacy-policy.md", post_type="pages")

    print("\n=== Aboutページを投稿（page）===")
    create_post(base / "about.md", post_type="pages")
