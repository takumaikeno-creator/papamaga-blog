#!/usr/bin/env python3
import os
import requests
import tempfile
from pathlib import Path

WP_URL = "https://www.papa-maga.online"
WP_USER = os.environ.get("WP_USER", "takuma")
WP_PASS = os.environ.get("WP_APP_PASS", "t5dw FCKy iHnO cAiB Q2Zd dRe0")
AUTH = (WP_USER, WP_PASS)

PIXABAY_KEY = "55572949-49fea0ca03f86fca767474ce6"

def search_pixabay(query, lang="ja"):
    url = "https://pixabay.com/api/"
    params = {
        "key": PIXABAY_KEY,
        "q": query,
        "lang": lang,
        "image_type": "photo",
        "orientation": "horizontal",
        "category": "house",
        "min_width": 1200,
        "per_page": 5,
        "safesearch": "true",
    }
    r = requests.get(url, params=params)
    data = r.json()
    hits = data.get("hits", [])
    if not hits:
        # fallback: English search
        params["lang"] = "en"
        params["q"] = query.replace("ロボット掃除機", "robot vacuum cleaner").replace("家事", "housework")
        r = requests.get(url, params=params)
        hits = r.json().get("hits", [])
    return hits

def upload_image_to_wp(image_url, filename, alt_text):
    img_data = requests.get(image_url).content
    upload_url = f"{WP_URL}/?rest_route=/wp/v2/media"
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Content-Type": "image/jpeg",
    }
    r = requests.post(upload_url, auth=AUTH, headers=headers, data=img_data)
    if r.status_code in (200, 201):
        media = r.json()
        # Set alt text
        requests.post(
            f"{WP_URL}/?rest_route=/wp/v2/media/{media['id']}",
            auth=AUTH,
            json={"alt_text": alt_text, "caption": "Photo via Pixabay"}
        )
        return media["id"]
    else:
        print(f"アップロード失敗: {r.status_code} {r.text[:200]}")
        return None

def set_featured_image(post_id, media_id):
    url = f"{WP_URL}/?rest_route=/wp/v2/posts/{post_id}"
    r = requests.post(url, auth=AUTH, json={"featured_media": media_id})
    return r.status_code in (200, 201)

if __name__ == "__main__":
    print("🔍 Pixabayで画像を検索中...")
    hits = search_pixabay("robot vacuum cleaner home")
    if not hits:
        hits = search_pixabay("cleaning home family")

    if not hits:
        print("❌ 画像が見つかりませんでした")
        exit(1)

    best = hits[0]
    print(f"✅ 画像を選定: {best['pageURL']}")
    print(f"   サイズ: {best['imageWidth']}x{best['imageHeight']}")

    print("📤 WordPressにアップロード中...")
    media_id = upload_image_to_wp(
        best["largeImageURL"],
        "robot-vacuum-featured.jpg",
        "ロボット掃除機で家事を効率化するパパのイメージ"
    )
    if not media_id:
        exit(1)
    print(f"✅ メディアアップロード完了 (ID: {media_id})")

    print("🖼️  アイキャッチ画像を設定中...")
    if set_featured_image(99, media_id):
        print("✅ アイキャッチ画像の設定完了！")
        print(f"   記事URL: https://www.papa-maga.online/?p=99")
    else:
        print("❌ アイキャッチ設定に失敗しました")
