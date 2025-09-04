import requests
import json

webhook_url = "https://defaultd4398d3154f8451088beffc628e4e5.14.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/bf62fe1628454ec48672433674bdca5c/triggers/manual/paths/invoke/?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=r6gY2Z7mrH27PNiWDh09CrUC2rw04DOC1T9GI-3E-EE"
payload = {
    "title": "🔔 알림봇 테스트",
    "message": "이 메시지는 Power Automate Workflows를 통해 전송되었습니다."
}

resp = requests.post(webhook_url, headers={"Content-Type": "application/json"}, data=json.dumps(payload))
print(resp.status_code, resp.text)
