import requests
import json
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from PIL import Image
import pytesseract

def main():
    flow_url = os.environ.get("FLOW_URL")
    if not flow_url:
        print("❌ FLOW_URL 환경변수가 없습니다.")
        return

    # Tesseract 설치 경로 설정 (Windows 환경)
    # macOS/Linux 사용자는 brew install tesseract 또는 apt-get install tesseract-ocr
    # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    naver_url = "https://map.naver.com/p/search/%EB%B0%A5%EC%A7%93%EB%8A%94%EB%B6%80%EC%97%84/place/1578060862"
    image_xpath = '//*[@id="app-root"]/div/div/div[6]/div/div[1]/div/ul/li[1]/div[2]/div/a/img'
    
    # Chrome WebDriver 설정 (headless 모드)
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument('disable-gpu')
    options.add_argument('lang=ko_KR')
    
    driver = None
    try:
        driver = webdriver.Chrome(options=options)
        print("🌐 네이버 플레이스 페이지에 접속합니다...")
        driver.get(naver_url)
        time.sleep(5)  # 페이지 로딩 대기
        
        # 이미지 요소 찾기
        img_element = driver.find_element(By.XPATH, image_xpath)
        image_url = img_element.get_attribute("src")
        
        if not image_url:
            print("❌ 이미지를 찾을 수 없습니다.")
            return

        print(f"✅ 이미지 URL을 찾았습니다: {image_url}")

        # 이미지 다운로드
        print("📥 이미지를 다운로드합니다...")
        response = requests.get(image_url)
        if response.status_code != 200:
            print(f"❌ 이미지 다운로드 실패. 상태 코드: {response.status_code}")
            return
        
        # 다운로드된 이미지로 PIL Image 객체 생성
        img = Image.open(BytesIO(response.content))

        # OCR을 이용한 텍스트 추출
        print("🔍 이미지에서 텍스트를 분석합니다...")
        menu_text = pytesseract.image_to_string(img, lang='kor+eng')
        
        if not menu_text.strip():
            print("❌ 이미지에서 메뉴를 추출하지 못했습니다.")
            message = "오늘은 메뉴 이미지를 분석할 수 없습니다. 직접 확인해 주세요."
        else:
            # 추출된 텍스트를 줄바꿈 기준으로 다듬기
            menu_lines = [line.strip() for line in menu_text.split('\n') if line.strip()]
            menu_message = ", ".join(menu_lines)
            message = f"오늘의 메뉴는 다음과 같습니다: {menu_message}"

        payload = {
            "title": "🍽️ 오늘의 메뉴",
            "message": message,
            "image_url": image_url
        }

        resp = requests.post(
            flow_url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        print("상태 코드:", resp.status_code)
        print("응답:", resp.text)

    except Exception as e:
        print(f"❌ 오류가 발생했습니다: {e}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()
