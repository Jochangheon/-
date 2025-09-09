import os, requests, json

def main():
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        print("❌ HF_TOKEN 환경변수가 없습니다.")
        return

    model = "google/flan-t5-base"  # Inference API 지원 모델
    api_url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {hf_token}"}

    payload = {"inputs": "오늘 점심 메뉴 3가지를 추천해줘."}

    print("🤖 Hugging Face REST API 호출 중...")
    response = requests.post(api_url, headers=headers, json=payload)

    print("🔎 상태 코드:", response.status_code)
    try:
        print("✅ 응답:", response.json())
    except Exception:
        print("❌ 응답 텍스트:", response.text)

if __name__ == "__main__":
    main()
