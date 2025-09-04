import os
import json
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By

def crawl_image_from_naver(place_url: str) -> str:
    """네이버 플레이스 entryIframe에서 첫 번째 소식 이미지 URL 추출"""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")   # 창 없이 실행
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.get(place_url)

    # entryIframe 안으로 들어가기
    driver.switch_to.frame("entryIframe")
    time.sleep(3)  # 소식탭 로딩 대기

    image_url = None
    images = driver.find_elements(By.TAG_NAME, "img")
    for img in images:
        src = img.get_attribute("src")
        if src and "ldb-phinf.pstatic.net" in src:  # 업로드 이미지 서버
            image_url = src
            break

    driver.quit()
    return image_url


def send_image_to_teams(image_url: str, title="오늘의 소식 사진"):
    webhook_url = os.environ.get("TEAMS_WEBHOOK_URL")
    if not webhook_url:
        print("❌ TEAMS_WEBHOOK_URL 환경변수가 없습니다.")
        return

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
                        {"type": "TextBlock", "text": title, "weight": "Bolder", "size": "Medium"},
                        {"type": "Image", "url": image_url, "size": "Stretch"}
                    ]
                }
            }
        ]
    }

    resp = requests.post(webhook_url,
                         headers={"Content-Type": "application/json"},
                         data=json.dumps(payload))
    print("Teams 전송 상태:", resp.status_code, resp.text)


if __name__ == "__main__":
    place_url = "https://map.naver.com/p/entry/place/1578060862"
    image_url = crawl_image_from_naver(place_url)

    if image_url:
        print("크롤링한 이미지 URL:", image_url)
        send_image_to_teams(image_url, title="🍽️ 오늘의 메뉴")
    else:
        print("❌ 이미지를 찾지 못했습니다.")
