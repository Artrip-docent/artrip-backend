from django.core.management.base import BaseCommand
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import time

from exhibition.models import Exhibition  # 모델에 맞게 import

class Command(BaseCommand):
    help = '네이버 전시회 페이지를 크롤링해서 Exhibition 테이블에 저장합니다.'

    def handle(self, *args, **kwargs):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        service = Service("/usr/bin/chromedriver")
        driver = webdriver.Chrome(service=service, options=options)
        url = "https://search.naver.com/search.naver?query=전시회"
        driver.get(url)
        time.sleep(3)

        while True:
            cards = driver.find_elements(By.CLASS_NAME, "card_item")
            for e in cards:
                try:
                    img_url = e.find_element(By.CSS_SELECTOR, ".img_box img").get_attribute("src")
                    title = e.find_element(By.CSS_SELECTOR, ".img_box img").get_attribute("alt")

                    dates = e.find_elements(By.CLASS_NAME, "info_date")
                    start_date = dates[0].text.strip() if len(dates) > 0 else ""
                    end_date = dates[1].text.strip() if len(dates) > 1 else ""

                    try:
                        place = e.find_elements(By.CLASS_NAME, "no_ellip")[1].text.strip()
                    except:
                        place = ""

                    if not Exhibition.objects.filter(title=title, start_date=start_date, location=place).exists():
                        Exhibition.objects.create(
                            title=title,
                            start_date=start_date,
                            end_date=end_date,
                            location=place,
                            image_url=img_url
                        )

                    self.stdout.write(self.style.SUCCESS(f'✔️ 삽입: {title}'))
                except Exception as ex:
                    self.stdout.write(self.style.ERROR(f'❗ 에러: {ex}'))

            try:
                next_btn = driver.find_element(By.CLASS_NAME, "pg_next")
                if "on" in next_btn.get_attribute("class"):
                    next_btn.click()
                    time.sleep(2)
                else:
                    break
            except NoSuchElementException:
                break

        driver.quit()
        self.stdout.write(self.style.SUCCESS('🎉 크롤링 완료'))

