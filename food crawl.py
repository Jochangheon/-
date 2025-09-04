import os
import time
import json
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

def crawl_image():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # GUI 없이 실행
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service("/usr/bin/chromedriver"), options=options)

    driver.get("https://map.naver.com/p/entry/place/1578060862")

    # entryIframe으로 전환
    driver.switch_to.frame("entryIframe")
    time.sleep(3)

    image_url = None
    images = driver.find_elements(By.TAG_NAME, "img")
    for img in images:
        src = img.get_attribute("src")
        if src and "ldb-phinf.pstatic.net" in src:
            image_url = src
            break

    driver.quit()
    return image_url


def send_to_teams(image_url):
    webhook_url = os.environ.get("TEAMS_WEBHOOK_URL")
    if not webhook_url:
        print("❌ TEAMS_WEBHOOK_URL 환경변수가 없습니다.")
        return

    if not image_url:
        payload = {"text": "❌ 오늘 이미지를 가져오지 못했습니다."}
    else:
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
                            {"type": "TextBlock", "text": "🍽️ 오늘의 메뉴", "weight": "Bolder", "size": "Medium"},
                            {"type": "Image", "url": image_url, "size": "Stretch"}
                        ]
                    }
                }
            ]
        }

    resp = requests.post(
        webhook_url,
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload)
    )
    print("Teams 전송 상태:", resp.status_code, resp.text)


if __name__ == "__main__":
    url = crawl_image()
    print("크롤링된 이미지:", url)
    send_to_teams(url)
