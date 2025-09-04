import requests
from bs4 import BeautifulSoup
import json
import os

def main():
    # ① 크롤링 (예시: Hacker News에서 첫 번째 헤드라인 가져오기)
    try:
        html = requests.get("https://news.ycombinator.com/").text
        soup = BeautifulSoup(html, "html.parser")
        headline = soup.select_one(".titleline a").get_text()
    except Exception as e:
        headline = f"크롤링 실패: {e}"

    # ② GitHub Secrets에서 Webhook URL 불러오기
    webhook_url = os.environ.get("TEAMS_WEBHOOK_URL")
    if not webhook_url:
        print("❌ TEAMS_WEBHOOK_URL 환경변수가 없습니다.")
        return

    # ③ 메시지 구성
    payload = {
        "title": "🔔 자동 뉴스 알림",
        "message": headline
    }

    # ④ Teams Webhook POST
    try:
        resp = requests.post(
            webhook_url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        print("전송 상태:", resp.status_code, resp.text)
    except Exception as e:
        print("❌ 전송 중 오류:", e)


if __name__ == "__main__":
    main()
