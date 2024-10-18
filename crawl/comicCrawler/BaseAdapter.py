import cchardet
from curl_cffi.requests import get
from urllib.parse import urljoin

class BaseAdapter:
    def __init__(self, features):
        self.features = features
        self.domain = features['baseUrl']
        self.config = {
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
                "Referer": self.domain
            },
        }
    
    def get(self, target: str):
        if "http" not in target:
            target = urljoin(self.domain, target)
        response = get(target, headers=self.config['headers'])
        encoding = cchardet.detect(response.content)['encoding']
        response.encoding = encoding
        return response