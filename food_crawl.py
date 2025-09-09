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

def check_hf_token_permissions(hf_token):
    """Hugging Face 토큰 권한 확인"""
    print("🔍 Hugging Face 토큰 권한 확인 중...")
    api_url = "https://huggingface.co/api/whoami-v2"
    headers = {"Authorization": f"Bearer {hf_token}"}
    
    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print("✅ 토큰 유효성 확인 완료")
            print(f"   사용자명: {result.get('name', 'N/A')}")
            return True
        else:
            print(f"❌ 토큰 확인 실패: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 토큰 확인 중 오류: {e}")
        return False

def analyze_image_with_multimodal_models(image_url, hf_token):
    """멀티모달 모델을 사용한 이미지 분석"""
    
    # 이미지 캡셔닝 및 멀티모달 모델들[1][8]
    multimodal_models = [
        "Salesforce/blip-image-captioning-base",  # 이미지 캡셔닝
        "Salesforce/blip-image-captioning-large", # 더 큰 이미지 캡셔닝 모델
        "nlpconnect/vit-gpt2-image-captioning",   # ViT + GPT2 조합
        "microsoft/git-base-coco"                 # Microsoft의 이미지 캡셔닝
    ]
    
    for model in multimodal_models:
        print(f"🤖 {model} 모델로 이미지 분석 시도...")
        api_url = f"https://api-inference.huggingface.co/models/{model}"
        headers = {"Authorization": f"Bearer {hf_token}"}
        
        try:
            # 이미지를 직접 다운로드하여 바이너리로 전송[8]
            img_response = requests.get(image_url, timeout=10)
            if img_response.status_code != 200:
                print(f"   ❌ 이미지 다운로드 실패: {img_response.status_code}")
                continue
                
            # 이미지를 바이너리 데이터로 API에 전송
            for attempt in range(3):
                try:
                    print(f"   시도 {attempt + 1}/3...")
                    
                    # 이미지 캡셔닝 API 호출
                    resp = requests.post(
                        api_url, 
                        headers=headers, 
                        data=img_response.content,  # 이미지 바이너리 데이터 직접 전송
                        timeout=30
                    )
                    print(f"   응답 상태: {resp.status_code}")
                    
                    if resp.status_code == 200:
                        result = resp.json()
                        print("✅ 이미지 분석 성공!")
                        print("결과:", json.dumps(result, ensure_ascii=False, indent=2))
                        
                        # 결과에서 메뉴 관련 키워드 추출
                        if isinstance(result, list) and len(result) > 0:
                            caption = result.get('generated_text', '')
                            print(f"🍽️ 생성된 설명: {caption}")
                            
                            # 추가로 메뉴 관련 정보 추출을 위한 텍스트 분석
                            menu_keywords = extract_menu_keywords(caption)
                            if menu_keywords:
                                print(f"🔍 추출된 메뉴 키워드: {menu_keywords}")
                        
                        return result
                        
                    elif resp.status_code == 404:
                        print(f"   ❌ {model} 모델 사용 불가")
                        break
                    elif resp.status_code == 503:
                        print("   ⏳ 모델 로딩 중...")
                        time.sleep(10)
                    else:
                        print(f"   ⚠️ 상태: {resp.status_code}, 응답: {resp.text}")
                        time.sleep(2)
                        
                except requests.exceptions.RequestException as e:
                    print(f"   ❌ 요청 오류: {e}")
                    time.sleep(2)
                    
        except Exception as e:
            print(f"   ❌ 모델 {model} 처리 중 오류: {e}")
            continue
    
    print("❌ 모든 멀티모달 모델 시도 실패")
    return None

def extract_menu_keywords(text):
    """텍스트에서 메뉴 관련 키워드 추출"""
    menu_keywords = ['food', 'dish', 'meal', 'restaurant', 'menu', 'rice', 'soup', 'chicken', 'beef', 'pork', 'vegetable', 'noodle', '음식', '메뉴', '식당', '밥', '국', '찌개', '볶음']
    found_keywords = []
    
    text_lower = text.lower()
    for keyword in menu_keywords:
        if keyword.lower() in text_lower:
            found_keywords.append(keyword)
    
    return found_keywords

def main():
    flow_url = os.environ.get("FLOW_URL")
    hf_token = os.environ.get("HF_TOKEN")
    print("FLOW_URL:", "✅ 설정됨" if flow_url else "❌ 없음")
    print("HF_TOKEN:", "✅ 설정됨" if hf_token else "❌ 없음")
    
    if not hf_token:
        print("❌ HF_TOKEN 환경변수가 없습니다.")
        return
    
    if not check_hf_token_permissions(hf_token):
        print("❌ 토큰 권한 확인 실패. 프로그램을 종료합니다.")
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
        print(f"✅ 이미지 저장됨: {img_path}")

        # 멀티모달 모델로 이미지 분석
        result = analyze_image_with_multimodal_models(image_url, hf_token)
        
        if result:
            print("🎉 이미지 분석 완료!")
            # 추가 처리: 결과를 바탕으로 메뉴 정보 구조화
            structured_menu = structure_menu_info(result)
            if structured_menu:
                print("📋 구조화된 메뉴 정보:")
                print(json.dumps(structured_menu, ensure_ascii=False, indent=2))
        else:
            print("❌ 이미지 분석 실패")
        
    except Exception as e:
        print("❌ 오류 발생:", repr(e))
        traceback.print_exc()
    
    finally:
        if driver:
            driver.quit()

def structure_menu_info(analysis_result):
    """분석 결과를 구조화된 메뉴 정보로 변환"""
    if not analysis_result or not isinstance(analysis_result, list):
        return None
    
    structured_info = {
        "description": "",
        "detected_items": [],
        "confidence": 0.0
    }
    
    if len(analysis_result) > 0 and 'generated_text' in analysis_result:
        structured_info["description"] = analysis_result['generated_text']
        structured_info["confidence"] = analysis_result.get('score', 0.0)
        
        # 간단한 키워드 기반 메뉴 아이템 추출
        text = analysis_result['generated_text']
        menu_items = extract_menu_keywords(text)
        structured_info["detected_items"] = menu_items
    
    return structured_info

if __name__ == "__main__":
    main()
