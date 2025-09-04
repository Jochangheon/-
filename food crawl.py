import requests, json, os

def main():
    flow_url = os.environ.get("FLOW_URL")  # GitHub Secrets에서 넘어옴
    if not flow_url:
        print("❌ FLOW_URL 환경변수가 없습니다.")
        return

    payload = {
        "title": "🍽️ 오늘의 메뉴",
        "message": "점심 사진 확인하세요",
        "image_url": "https://ldb-phinf.pstatic.net/test.jpg"
    }

    resp = requests.post(
        flow_url,
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload)
    )
    print("상태 코드:", resp.status_code)
    print("응답:", resp.text)

if __name__ == "__main__":
    main()
