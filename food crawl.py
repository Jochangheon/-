import requests
import json
import os
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
from huggingface_hub import InferenceClient


def main():
    # Flow URL
    flow_url = os.environ.get("FLOW_URL")
    if not flow_url:
        print("❌ FLOW_URL 환경변수가 없습니다.")
        return

    # Hugging Face 토큰
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        print("❌ HF_TOKEN 환경변수가 없습니다. Hugging Face Access Token을 설정하세요.")
        return

    # 네이버 플레이스 URL
    naver_url = "https://map.naver.com/p/search/%EB%B0%A5%EC%A7%93%EB%8A%94%20%EB%B6%80%EC%97%8C/place/1578060862"

    # 크롬 옵션
    options = webdriver.ChromeOptions()
    options.binary_location = "/usr/bin/google-chrome"
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--lang=ko_KR")

    driver = None
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        print("🌐 네이버 플레이스 페이지 접속...")
        driver.get(naver_url)

        wait = WebDriverWait(driver, 15)

        # entryIframe 전환
        print("🔄 entryIframe 전환...")
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "entryIframe")))
        print("✅ entryIframe 전환 성공")

        # 메뉴 이미지 탐색
        print("🔍 메뉴 이미지 탐색...")
        img_element = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.place_section img"))
        )
        image_url = img_element.get_attribute("src")

        if not image_url:
            print("❌ 이미지 URL을 찾지 못했습니다.")
            return
        print(f"✅ 이미지 URL: {image_url}")

        # 이미지 다운로드 (검증용)
        response = requests.get(image_url, timeout=10)
        img = Image.open(BytesIO(response.content))
        img_path = "/tmp/menu.jpg"
        img.save(img_path)

        # Hugging Face AI 호출
        print("🤖 Hugging Face AI 호출 중...")
        client = InferenceClient(model="Qwen/Qwen-VL", token=hf_token)

        prompt = f"""
        아래 이미지에 나온 음식 메뉴 이름만 뽑아서 JSON 배열로 출력해줘.
        예시: ["김치찌개","된장찌개","비빔밥"]

        이미지 URL: {image_url}
        """

        response = client.text_generation(prompt, max_new_tokens=512)

        # 응답 처리
        try:
            menus = json.loads(response.strip())
        except Exception:
            menus = [line.strip() for line in response.split("\n") if line.strip()]

        print("\n===== AI 추출 결과 =====")
        for idx, menu in enumerate(menus, 1):
            print(f"{idx}. {menu}")
        print("=========================\n")

        # Flow 전송 Payload
        payload = {
            "title": "🍽️ 오늘의 메뉴 (AI 인식)",
            "message": "\n".join(menus),
            "image_url": image_url
        }

        print("===== 전송할 Payload =====")
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        print("=========================\n")

        # Flow API 전송
        resp = requests.post(
            flow_url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            timeout=10,
        )
        print("상태 코드:", resp.status_code)
        print("응답:", resp.text)

    except Exception as e:
        print("❌ 오류 발생:", e)
    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    main()
