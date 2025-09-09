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

        wait = WebDriverWait(driver, 30)
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

        # 확실히 작동하는 모델들 목록 (우선순위 순)
        working_models = [
            "facebook/bart-large-cnn",  # 검증된 작동 모델
            "microsoft/DialoGPT-medium",
            "gpt2"  # 백업 옵션
        ]

        for model in working_models:
            print(f"🤖 {model} 모델 시도 중...")
            api_url = f"https://api-inference.huggingface.co/models/{model}"
            headers = {
                "Authorization": f"Bearer {hf_token}",
                "Content-Type": "application/json"
            }
            
            # 모델별 적절한 payload 설정
            if "bart" in model.lower():
                payload = {
                    "inputs": f"이 음식점 메뉴 이미지에서 음식 이름들을 추출해주세요: {image_url}. 한국 음식 메뉴를 JSON 형태로 정리해주세요.",
                    "parameters": {
                        "max_length": 200,
                        "min_length": 30
                    }
                }
            else:
                payload = {
                    "inputs": f"메뉴판 이미지 분석: {image_url}. 음식 이름 목록:"
                }

            success = False
            for attempt in range(3):
                try:
                    print(f"   시도 {attempt + 1}/3...")
                    resp = requests.post(api_url, headers=headers, json=payload, timeout=30)
                    print(f"   응답 상태: {resp.status_code}")

                    if resp.status_code == 200:
                        result = resp.json()
                        print("✅ API 호출 성공!")
                        print("응답:", json.dumps(result, ensure_ascii=False, indent=2))
                        success = True
                        break
                    elif resp.status_code == 404:
                        print(f"   ❌ {model} 모델 사용 불가 (404)")
                        break
                    elif resp.status_code == 503:
                        print("   ⏳ 모델 로딩 중, 재시도...")
                        time.sleep(10)
                    else:
                        print(f"   ⚠️ 상태 코드: {resp.status_code}, 응답: {resp.text}")
                        time.sleep(2)
                        
                except requests.exceptions.RequestException as e:
                    print(f"   ❌ 요청 오류: {e}")
                    time.sleep(2)
            
            if success:
                break
        else:
            print("❌ 모든 모델 시도 실패")
        
    except Exception as e:
        print("❌ 오류 발생:", repr(e))
        traceback.print_exc()
    
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()
