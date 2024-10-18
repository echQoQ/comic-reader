from bs4 import BeautifulSoup
from urllib.parse import urljoin
from .BaseAdapter import BaseAdapter

class Handler0(BaseAdapter):
    def search(self, keyword: str = ""):
        url = self.features['search']['url'].format(keyword=keyword)
        html = self.get(url).text
        soup = BeautifulSoup(html, 'lxml')
        comic_list = soup.select(self.features['search']['comic_item_selector'])

        return [
            {
                "title": x.select_one(self.features['search']['title_selector']).get_text(strip=True),
                "url": x.select_one(self.features['search']['url_selector'])['href'],
                "cover_img": x.select_one(self.features['search']['cover_img'])[self.features['search']['cover_img_attribute']]
            }
            for x in comic_list
        ]

    def crawl_chapters(self, comic_url):
        html = self.get(comic_url).text
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
        html = self.get(chapter_href).text
        soup = BeautifulSoup(html, 'lxml')
        images = []
        image_soup_list = soup.select(self.features['images']['selector'])

        for image_soup in image_soup_list:
            src = image_soup[self.features['images']['src_attribute']]
            images.append(urljoin(self.domain, src) if 'http' not in src else src)

        return images
