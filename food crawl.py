from huggingface_hub import InferenceClient
import os

def main():
    # Hugging Face 토큰 불러오기
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        print("❌ HF_TOKEN 환경변수가 없습니다.")
        return

    try:
        # 간단한 텍스트 모델 (gpt2) 호출
        client = InferenceClient(model="gpt2", token=hf_token)

        prompt = "오늘 저녁 메뉴 추천해줘:"
        print("🤖 Hugging Face API 호출 중...")
        response = client.text_generation(prompt, max_new_tokens=50)

        print("✅ 응답 결과:")
        print(response)

    except Exception as e:
        import traceback
        print("❌ 오류 발생:", repr(e))
        traceback.print_exc()


if __name__ == "__main__":
    main()
