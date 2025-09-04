from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

def crawl_image():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # 창 안 띄움
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # GitHub Actions용 경로: /usr/bin/chromedriver
    driver = webdriver.Chrome(service=Service("/usr/bin/chromedriver"), options=options)

    driver.get("https://map.naver.com/p/entry/place/1578060862")

    # entryIframe으로 전환
    driver.switch_to.frame("entryIframe")
    time.sleep(3)

    image_url = None
    images = driver.find_elements(By.TAG_NAME, "img")
    for img in images:
        src = img.get_attribute("src")
        if src and "ldb-phinf.pstatic.net" in src:
            image_url = src
            break

    driver.quit()
    return image_url
