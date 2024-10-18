import os
import json
import re
from curl_cffi import requests
from base64 import b64decode
from .adapter import Adapter
from urllib.parse import urljoin
import logging
import shutil


def safe_name(dir_name):
    invalid_chars = r'[\ <>:"/\\|?*]'
    sanitized_name = re.sub(invalid_chars, '_', dir_name.strip())
    return sanitized_name

def getRealPathFromMetaJson(basePath, name):
	jsonData = {}
	if not os.path.exists(os.path.join(basePath, 'metadata.json')):
		jsonData = {
			name: {
				"path": safe_name(name)
			}
		}
		with open(os.path.join(basePath,'metadata.json'), 'w+', encoding='utf-8') as f:
			json.dump(jsonData, f, ensure_ascii=False, indent=4)
		return safe_name(name)
	else:
		with open(os.path.join(basePath, 'metadata.json'), 'r', encoding='utf-8') as f:
			jsonData = json.load(f)
			if name in jsonData:
				return jsonData[name]['path']
			else:
				jsonData[name] = {
					"path": safe_name(name)
				}
		with open(os.path.join(basePath, 'metadata.json'), 'w+', encoding='utf-8') as f:
			json.dump(jsonData, f, ensure_ascii=False, indent=4)
		return safe_name(name)

def download_image(url, path):
	try:
		response = requests.get(url)
		if response.status_code == 200:
			with open(path, 'wb') as file:
				file.write(response.content)
	except Exception as e:
		print(f"An error occurred: {e}")

class Crawler():
	def __init__(self, json_file) -> None:
		self.json_file = json_file
	
	def search(self, keyword:str="", adapter_name:str='biqu'):
		if keyword == "":
			return []
		return Adapter(adapter_name, self.json_file).search(keyword)
	
	def loadChapters(self, comicUrl, adapter_name:str='biqu'):
		return Adapter(adapter_name, self.json_file).crawl_chapters(comicUrl)

	def loadImages(self, chapterHref,adapter_name:str='biqu'):
		return Adapter(adapter_name, self.json_file).crawl_images(chapterHref)
	
	def downloadChapter(self, comic_name, chapter_name,chapter_href, comic_base_path, adapter):
		images = self.loadImages(chapter_href, adapter)
		comic_path = os.path.join(comic_base_path, getRealPathFromMetaJson(comic_base_path, comic_name))
		os.makedirs(comic_path, exist_ok=True)
		#print(comic_path)
		chapter_path = os.path.join(comic_path, getRealPathFromMetaJson(comic_path, chapter_name))
		os.makedirs(chapter_path, exist_ok=True)
		#print(chapter_path)

		jsonData = {}
		with open(os.path.join(comic_path, 'metadata.json'), 'r', encoding='UTF-8') as f:
			jsonData = json.load(f)
		
		jsonData[chapter_name]['images'] = []
		tasks = []

		for i, image_url in enumerate(images, start=1):
			image_name = f"{i:03d}.png"
			jsonData[chapter_name]['images'].append(image_name)
			image_path = os.path.join(chapter_path, image_name)
			download_image(image_url, image_path)

		with open(os.path.join(comic_path, 'metadata.json'), 'w+', encoding='utf-8') as f:
			json.dump(jsonData, f, ensure_ascii=False, indent=4)
	
	def load_downloaded_comics(self, comic_base_path):
		try:
			jsonData = {}
			if ( not os.path.exists(os.path.join(comic_base_path, 'metadata.json'))):
				return []
			with open(os.path.join(comic_base_path, 'metadata.json'), 'r', encoding='utf-8') as f:
				jsonData = json.load(f)
			return jsonData.keys()
		except Exception as e:
			logging.exception(e)
			return []
	
	def load_downloaded_chapters(self, comic_base_path, comic_name):
		try:
			if ( not os.path.exists(os.path.join(comic_base_path, 'metadata.json'))):
				return []
			if ( not os.path.exists(os.path.join(comic_base_path, comic_name,'metadata.json'))):
				return []
			with open(os.path.join(comic_base_path, 'metadata.json'), 'r', encoding='utf-8') as f:
				jsonData = json.load(f)
				flag = False
				comic_name = safe_name(comic_name)
				for value in jsonData.values():
					if value['path'] == comic_name:
						flag = True
						break
				if not flag:
					return []
				with open(os.path.join(comic_base_path, comic_name,'metadata.json'), 'r', encoding='utf-8') as f:
					jsonData = json.load(f)
					return jsonData.keys()
		except Exception as e:
			logging.exception(e)
			return []
    
	def load_downloaded_images(self, comic_base_path, comic_name, chapter_name):
		try:
			with open(os.path.join(comic_base_path, 'metadata.json'), 'r', encoding='utf-8') as f:
				jsonData = json.load(f)
				flag = False
				comic_name = safe_name(comic_name)
				for (key, value) in jsonData.items():
					if value['path'] == comic_name:
						flag = True
						break
				if not flag:
					return []
				with open(os.path.join(comic_base_path, comic_name, 'metadata.json'), 'r', encoding='utf-8') as f2:
					jsonData2 = json.load(f2)
					flag = False
					for (key, value) in jsonData2.items():
						if value['path'] == safe_name(chapter_name):
							flag = True
							break
					if not flag:
						return []
					images = jsonData2[chapter_name]['images']
					chapter_path = jsonData2[chapter_name]['path']
					image_urls = ['/'.join(['public','comics', comic_name, chapter_path, image_name]) for image_name in images]
					return image_urls
		except Exception as e:
			logging.exception(e)
			return []
		
	def delete_comic(self, comic_base_path, comic_name):
		comic_path = os.path.join(comic_base_path, getRealPathFromMetaJson(comic_base_path, comic_name))
		if os.path.exists(comic_path):
			shutil.rmtree(comic_path)
		self._update_metadata(comic_base_path, comic_name, remove=True)
	
	def delete_chapter(self, comic_base_path, comic_name, chapter_name):
		comic_path = os.path.join(comic_base_path, safe_name(comic_name))
		chapter_path = os.path.join(comic_path, safe_name(chapter_name))
		if os.path.exists(chapter_path):
			shutil.rmtree(chapter_path)
		self._update_metadata(os.path.join(comic_base_path, safe_name(comic_name)), comic_name, chapter_name, remove=True)  # 更新metadata.json

	def _update_metadata(self, comic_base_path, comic_name, chapter_name=None, remove=False):
		try:
			with open(os.path.join(comic_base_path ,'metadata.json'), 'r', encoding='utf-8') as f:
				jsonData = json.load(f)
			if chapter_name:
				if remove:
					del jsonData[chapter_name]
			else:
				if remove:
					del jsonData[comic_name]
				else:
					# 更新整个漫画信息，这里可以根据需要添加更新逻辑
					pass
			with open(os.path.join(comic_base_path, 'metadata.json'), 'w+', encoding='utf-8') as f:
				json.dump(jsonData, f, ensure_ascii=False, indent=4)
		except Exception as e:
			logging.exception(e)
