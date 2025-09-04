import requests
from bs4 import BeautifulSoup
import json
import os

def main():
    # ① 크롤링 (예: 네이버 플레이스 소식탭 이미지)
    try:
        url = "https://map.naver.com/p/entry/place/1578060862"
        headers = {"User-Agent": "Mozilla/5.0"}
        html = requests.get(url, headers=headers).text
        soup = BeautifulSoup(html, "html.parser")

        # <img> 태그 중 네이버 place 이미지 서버(ldb-phinf) 필터링
        img_tag = soup.find("img", src=lambda x: x and "ldb-phinf.pstatic.net" in x)
        if img_tag:
            image_url = img_tag["src"]
        else:
            image_url = None
    except Exception as e:
        image_url = None
        print("크롤링 실패:", e)

    # ② GitHub Secrets에서 Webhook URL 불러오기
    webhook_url = os.environ.get("TEAMS_WEBHOOK_URL")
    if not webhook_url:
        print("❌ TEAMS_WEBHOOK_URL 환경변수가 없습니다.")
        return

    # ③ Adaptive Card 메시지 구성
    if image_url:
        payload = {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": {
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "version": "1.4",
                        "body": [
                            {"type": "TextBlock", "text": "오늘의 소식 사진", "weight": "Bolder", "size": "Medium"},
                            {"type": "Image", "url": image_url, "size": "Stretch"}
                        ]
                    }
                }
            ]
        }
    else:
        payload = {
            "text": "❌ 이미지를 가져오지 못했습니다."
        }

    # ④ Teams Webhook POST
    try:
        resp = requests.post(
            webhook_url,
            heade
