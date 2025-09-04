import requests
import json

# Power Automate Flow에서 발급받은 HTTP POST URL 넣으세요
FLOW_URL = "https://defaultd4398d3154f8451088beffc628e4e5.14.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/bf62fe1628454ec48672433674bdca5c/triggers/manual/paths/invoke/?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=r6gY2Z7mrH27PNiWDh09CrUC2rw04DOC1T9GI-3E-EE"

def main():
    payload = {
        "title": "🍽️ 오늘의 메뉴",
        "message": "점심 사진 확인하세요",
        "image_url": "https://ldb-phinf.pstatic.net/20250904_103/1756947656431VPHgD_JPEG/1000024861.jpg"
    }

    resp = requests.post(
        FLOW_URL,
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload)
    )

    print("상태 코드:", resp.status_code)
    print("응답:", resp.text)

if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
