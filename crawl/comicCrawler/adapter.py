import os
import json
import cchardet
from curl_cffi.requests import get
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class Adapter():
	def __init__(self, name:str, json_file):
		self.name = name
		self.features = self.load_features(name, json_file)
		self.domain = self.features['baseUrl']
		self.config = {
			"headers"	:{
				"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
				"Referer"	: self.domain
			},
		}

	def load_features(self, name, json_file):
		with open(json_file, 'r', encoding='utf-8') as f:
			return json.load(f)[name]

	def search(self, keyword:str = ""):
		url = self.features['search']['url'].format(keyword=keyword)
		html = self.get(url).text
		soup = BeautifulSoup(html, 'html.parser')
		comic_list = soup.select(self.features['search']['comic_item_selector'])

		if not comic_list:
			return []
		return [
            {
                "title": x.select_one(self.features['search']['title_selector']).get_text(strip=True),
                "url": x.select_one(self.features['search']['url_selector'])['href'],
				"cover_img": x.select_one(self.features['search']['cover_img']).get(self.features['search']['cover_img_attribute'], '')
            }
            for x in comic_list
        ]
	def crawl_chapters(self, comic_url):
		html = self.get(comic_url).text
		soup = BeautifulSoup(html, 'html.parser')
		chapter_soup_list = soup.select(self.features['chapters']['chapter_item_selector'])

		return [
			{
				"title": x.select_one(self.features['chapters']['chapter_title_selector']).get_text(strip=True),
				"href": x.select_one(self.features['chapters']['chapter_url_selector'])[self.features['chapters']['href_selector']]
			}
			for x in chapter_soup_list
		]

	def crawl_images(self, chapter_href):
		html = self.get(chapter_href).text
		soup = BeautifulSoup(html, 'html.parser')
		images = []
		image_soup_list = soup.select(self.features['images']['selector'])

		for image_soup in image_soup_list:
			src = image_soup[self.features['images']['src_attribute']]
			if 'http' in src:
				images.append(src)
			else:
				images.append(urljoin(self.domain, src))

		return images

	def get(self, target:str):
		if "http" not in target:
			target = urljoin(self.domain,target)
		response = get(target,headers=self.config['headers'])
		encoding = cchardet.detect(response.content)['encoding']
		response.encoding = encoding
		return response



