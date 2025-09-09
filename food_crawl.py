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
import traceback
import time

def main():
    flow_url = os.environ.get("FLOW_URL")
    hf_token = os.environ.get("HF_TOKEN")
    print("FLOW_URL:", "✅ 설정됨" if flow_url else "❌ 없음")
    print("HF_TOKEN:", "✅ 설정됨" if hf_token else "❌ 없음")
    if not hf_token:
        print("❌ HF_TOKEN 환경변수가 없습니다.")
        return

    naver_url = "https://map.naver.com/p/search/%EB%B0%A5%EC%A7%93%EB%8A%94%20%EB%B6%80%EC%97%8C/place/1578060862"
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
        print("🔄 entryIframe 전환...")
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "entryIframe")))
        print("✅ entryIframe 전환 성공")

        print("🔍 메뉴 이미지 탐색...")
        img_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.place_section img")))
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

        # Hugging Face REST API 호출 (지원 모델 사용)
        model = "google/flan-t5-small"  # 모델 이름 확인 필요
        api_url = f"https://api-inference.huggingface.co/models/{model}"
        headers = {"Authorization": f"Bearer {hf_token}"}
        payload = {
            "inputs": f"다음은 음식점 메뉴 이미지 URL입니다: {image_url}\n"
                      f"이 메뉴판의 음식 이름만 JSON 배열로 정리해줘. 예시: [\"김치찌개\", \"된장찌개\", \"비빔밥\"]"
        }

        for attempt in range(5):  # 최대 5회 시도
            try:
                print("🤖 Hugging Face API 호출 중... (시도 {}/{})".format(attempt + 1, 5))
                resp = requests.post(api_url, headers=headers, json=payload, timeout=120)  # 타임아웃 늘림
                print("🔎 HF 응답 상태:", resp.status_code)

                resp.raise_for_status()  # HTTP 오류 발생 시 예외 발생
                
                result = resp.json()  # 응답 해석
                print("HF 응답 원본:", json.dumps(result, ensure_ascii=False, indent=2))
                break  # 성공적이면 루프를 빠져나옴
            except requests.exceptions.HTTPError as e:
                print("❌ 요청 실패: HTTP Error", e)
                print("응답 내용:", resp.text)
            except requests.exceptions.ReadTimeout:
                print("⏳ 타임아웃 발생, 재시도 대기 중...")
                time.sleep(2 ** attempt)  # 2의 제곱시간만큼 대기 (1, 2, 4, 8, 16초)
            except requests.exceptions.RequestException as e:
                print(f"❌ 요청 실패: {e}")
                print("응답 내용:", e.response.text if e.response else 'No response')
                break
        
    except Exception as e:
        print("❌ 오류 발생:", repr(e))
        traceback.print_exc()
    
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()
