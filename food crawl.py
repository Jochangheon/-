import os
import requests
import json

def main():
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        print("❌ HF_TOKEN 환경변수가 없습니다.")
        return

    model = "bigscience/bloomz-560m"   # ✅ Inference API 지원 모델
    api_url = f"https://api-inference.huggingface.co/models/google/embeddinggemma-300m"
    headers = {"Authorization": f"Bearer {hf_token}"}

    payload = {"inputs": "안녕하세요! 오늘 점심 메뉴 추천 3가지만 해줘."}

    print("🤖 Hugging Face API 호출 중...")
    resp = requests.post(api_url, headers=headers, json=payload, timeout=60)

    print("🔎 상태 코드:", resp.status_code)
    try:
        print("✅ 응답:", json.dumps(resp.json(), ensure_ascii=False, indent=2))
    except Exception:
        print("❌ 원문 응답:", resp.text)

if __name__ == "__main__":
    main()
