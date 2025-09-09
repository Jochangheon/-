import requests
import os

def main():
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        print("❌ HF_TOKEN 환경변수가 없습니다.")
        return

    model = "google/flan-t5-base"  # ✅ Inference API 지원 모델
    api_url = f"https://api-inference.huggingface.co/models/{model}"

    headers = {"Authorization": f"Bearer {hf_token}"}
    payload = {"inputs": "오늘 점심 메뉴 3가지를 추천해줘."}

    print("🤖 Hugging Face REST API 호출 중...")
    response = requests.post(api_url, headers=headers, json=payload)

    if response.status_code == 200:
        print("✅ 응답 결과:", response.json())
    else:
        print("❌ 오류:", response.status_code, response.text)


if __name__ == "__main__":
    main()
