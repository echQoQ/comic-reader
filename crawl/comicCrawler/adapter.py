import json
from .Handler0 import Handler0
from .Handler1 import Handler1


class Adapter:
    def __init__(self, name: str, json_file: str):
        self.features = self.load_features(name, json_file)
        if self.features['type'] == 0:
            self.handler = Handler0(self.features)
        elif self.features['type'] == 1:
            self.handler = Handler1(self.features)

    def load_features(self, name, json_file):
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)[name]

    def search(self, keyword: str = ""):
        return self.handler.search(keyword)

    def crawl_chapters(self, comic_url):
        return self.handler.crawl_chapters(comic_url)

    def crawl_images(self, chapter_href):
        return self.handler.crawl_images(chapter_href)
