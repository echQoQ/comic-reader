from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoAlertPresentException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin
from .BaseAdapter import BaseAdapter
from bs4 import BeautifulSoup
import time

class Handler1(BaseAdapter):
    def __init__(self, features):
        super().__init__(features)
        self.browser = self._init_selenium()

    def _init_selenium(self):
        options = Options()
        # options.add_argument('--headless') 
        return webdriver.Firefox(options=options)

    def search(self, keyword: str = ""):
        self.get(self.features['search']['url'].format(keyword=keyword))
        comic_list = self.browser.find_elements(By.CSS_SELECTOR, self.features['search']['comic_item_selector'])
        return [{"title": x.find_element(By.CSS_SELECTOR, self.features['search']['title_selector']).text.strip(),
                 "url": x.find_element(By.CSS_SELECTOR, self.features['search']['url_selector']).get_attribute('href'),
                 "cover_img": x.find_element(By.CSS_SELECTOR, self.features['search']['cover_img']).get_attribute(self.features['search']['cover_img_attribute'])} for x in comic_list]

    def crawl_chapters(self, comic_url):
        self.get(comic_url)
        
        html = self.browser.page_source
        soup = BeautifulSoup(html, 'lxml')
        # print(soup)
        chapter_list = soup.select(self.features['chapters']['chapter_item_selector'])

        return [
            {
                "title": BeautifulSoup(str(x), 'lxml').select_one(self.features['chapters']['chapter_title_selector']).get_text(strip=True),
                "href": BeautifulSoup(str(x), 'lxml').select_one(self.features['chapters']['chapter_url_selector'])[self.features['chapters']['href_selector']]
            }
            for x in chapter_list
        ]

    def crawl_images(self, chapter_href):
        self.get(chapter_href)
        images = []
        tp = self.features['images'].get('type', 1)
        if tp == 2: #单页式
            while True:
                images_container = self.browser.find_elements(By.CSS_SELECTOR, self.features['images']['selector'])
                for img in images_container:
                    images.append(img.get_attribute(self.features['images']['src_attribute']))
                next_button = self.browser.find_element(By.CSS_SELECTOR, self.features['images']['next_button_selector'])
                next_button.click()
                try:
                    alert = WebDriverWait(self.browser, 1).until(EC.alert_is_present())
                    alert.dismiss()
                    break
                except (NoAlertPresentException, TimeoutException):
                    continue
        elif tp == 1: #下拉式
            scroll_times = 5
            scroll_pause_time = 2
            for _ in range(scroll_times):
                self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(scroll_pause_time)
            images_container = self.browser.find_elements(By.CSS_SELECTOR, self.features['images']['selector'])
            for img in images_container:
                images.append(img.get_attribute(self.features['images']['src_attribute']))
        return images
    
    def get(self, url:str):
        if "http" not in url:
            url = urljoin(self.domain, url)
        self.browser.get(url)
    
    def __del__(self):
        self.browser.quit()
        return