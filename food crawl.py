import requests
import json

# Power Automate Flow에서 발급받은 HTTP POST URL 넣으세요
FLOW_URL = "https://defaultd4398d3154f8451088beffc628e4e5.14.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/bf62fe1628454ec48672433674bdca5c/triggers/manual/paths/invoke/?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=r6gY2Z7mrH27PNiWDh09CrUC2rw04DOC1T9GI-3E-EE"

def main():
    # ① 크롤링 부분 (여기서는 예시로 직접 URL 사용)
    #    → Selenium/BeautifulSoup으로 실제 이미지 주소 추출 가능
    image_url = "https://ldb-phinf.pstatic.net/20250904_103/1756947656431VPHgD_JPEG/1000024861.jpg"
    title = "🍽️ 오늘의 메뉴"
    message = "오늘 올라온 사진입니다"

    # ② Flow에 보낼 payload (스키마에 맞춰야 함)
    payload = {
        "title": title,
        "message": message,
        "image_url": image_url
    }

    # ③ HTTP POST 호출
    try:
        resp = requests.post(
            FLOW_URL,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        print("상태 코드:", resp.status_code)
        print("응답 내용:", resp.text)
    except Exception as e:
        print("❌ 전송 오류:", e)


if __name__ == "__main__":
    main()
