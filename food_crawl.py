import requests
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

def analyze_image_with_multimodal_models(image_url, hf_token):
    """멀티모달 모델을 사용한 이미지 분석"""
    
    # 실질적으로 Inference API에서 지원되는 이미지 캡셔닝 모 도시
    multimodal_models = [
        "google/vit-gpt2-image-captioning",  # 가능한 경우 사용하는 멀티모달 모델
        # 추가적으로 다른 모델들을 검토하고 사용합니다
    ]
    
    for model in multimodal_models:
        print(f"🤖 {model} 모델로 이미지 분석 시도...")
        api_url = f"https://api-inference.huggingface.co/models/{model}"
        headers = {"Authorization": f"Bearer {hf_token}"}
        
        try:
            # 이미지를 직접 다운로드하여 바이너리로 전송
            img_response = requests.get(image_url, timeout=10)
            img_response.raise_for_status()
                
            for attempt in range(3):
                try:
                    print(f"   시도 {attempt + 1}/3...")
                    resp = requests.post(
                        api_url, 
                        headers=headers, 
                        data=img_response.content,  # 이미지 바이너리 데이터 직접 전송
                        timeout=60  # 타임아웃 확대
                    )
                    print(f"   응답 상태: {resp.status_code}")
                    
                    if resp.status_code == 200:
                        result = resp.json()
                        print("✅ 이미지 분석 성공!")
                        print("결과:", result)
                        return result
                        
                    elif resp.status_code == 503:
                        print("   ⏳ 모델 로딩 중, 재시도...")
                        time.sleep(10)
                    else:
                        print(f"   ⚠️ 상태 코드: {resp.status_code}, 응답: {resp.text}")
                        time.sleep(2)
                        
                except requests.exceptions.RequestException as e:
                    print(f"   ❌ 요청 오류: {e}")
                    time.sleep(2)
                    
        except Exception as e:
            print(f"   ❌ 이미지 다운로딩 또는 모델 {model} 처리 중 오류: {e}")
            continue
    
    print("❌ 모든 멀티모달 모델 시도 실패")
    return None

def main():
    hf_token = os.environ.get("HF_TOKEN")
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

        # 멀티모달 모델로 이미지 분석
        analyze_image_with_multimodal_models(image_url, hf_token)
        
    except Exception as e:
        print("❌ 오류 발생:", repr(e))
        traceback.print_exc()
    
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()
