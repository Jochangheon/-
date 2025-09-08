import requests
import json
import os
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract


def main():
    # FLOW_URL 은 GitHub Secrets에서 받아옴
    flow_url = os.environ.get("FLOW_URL")
    if not flow_url:
        print("❌ FLOW_URL 환경변수가 없습니다. GitHub Secrets 설정을 확인하세요.")
        return

    # 네이버 플레이스 URL
    naver_url = "https://map.naver.com/p/search/%EB%B0%A5%EC%A7%93%EB%8A%94%20%EB%B6%80%EC%97%8C/place/1578060862"

    # Chrome WebDriver 옵션
    options = webdriver.ChromeOptions()
    options.binary_location = "/usr/bin/google-chrome"   # ✅ GitHub Actions용 크롬 경로 지정
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--lang=ko_KR")

    driver = None
    try:
        driver = webdriver.Chrome(options=options)
        print("🌐 네이버 플레이스 페이지 접속...")
        driver.get(naver_url)

        wait = WebDriverWait(driver, 15)

        # entryIframe 전환
        print("🔄 entryIframe 전환...")
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "entryIframe")))
        print("✅ entryIframe 전환 성공")

        # 메뉴 이미지 탐색 (소식의 첫 번째 이미지)
        print("🔍 메뉴 이미지 탐색...")
        img_element = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.place_section img"))
        )
        image_url = img_element.get_attribute("src")

        if not image_url:
            print("❌ 이미지 URL을 찾지 못했습니다.")
            return
        print(f"✅ 이미지 URL: {image_url}")

        # 이미지 다운로드
        response = requests.get(image_url, timeout=10)
        img = Image.open(BytesIO(response.content))

        # OCR 전처리
        img = img.convert("L")
        img = ImageEnhance.Contrast(img).enhance(2.0)
        img = img.filter(ImageFilter.SHARPEN)

        print("🔍 OCR 분석 시작...")
        menu_text = pytesseract.image_to_string(img, lang="kor+eng")

        if not menu_text.strip():
            message = "오늘은 메뉴 이미지를 분석할 수 없습니다. 직접 확인해 주세요."
            print("❌ OCR 결과 없음")
        else:
            menu_lines = [line.strip() for line in menu_text.split("\n") if line.strip()]
            menu_message = "\n".join(menu_lines)
            message = f"오늘의 메뉴는 다음과 같습니다:\n{menu_message}"

            print("\n===== OCR 추출 결과 =====")
            for idx, line in enumerate(menu_lines, 1):
                print(f"{idx}. {line}")
            print("=========================\n")

        # Payload 구성
        payload = {
            "title": "🍽️ 오늘의 메뉴",
            "message": message,
            "image_url": image_url,
        }

        # Payload 디버깅 출력
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
