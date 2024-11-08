from flask import Flask, request, jsonify
from flask_cors import CORS
from comicCrawler import Crawler
import sys
import os
import logging
import signal
import shutil
import glob

logging.basicConfig(filename='app.log', level=logging.INFO)

def clean_temp_directory():
    temp_dir = os.path.join(os.environ['TEMP'], '_MEI*')
    for temp_folder in glob.glob(temp_dir):
        if os.path.dirname(__file__) == temp_folder:
            continue
        shutil.rmtree(temp_folder, ignore_errors=True)

def signal_handler(sig, frame):
    print('Exiting gracefully...')
    clean_temp_directory()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# 初始化 Flask 应用并设置静态文件目录
app = Flask(__name__, static_folder=os.path.join(os.getcwd(), 'public'))
CORS(app, resources={r"*": {"origins": r"*"}})

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'message': 'Internal Server Error'}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'message': 'Resource not found'}), 404

@app.route('/search', methods=['POST'])
def handle_search():
    data = request.json
    keyword = data.get('keyword', '')
    adapter = data.get('adapter', 'biqu')
    crawler = Crawler(json_file)
    results = crawler.search(keyword, adapter)
    return jsonify(results)

@app.route('/load_chapters', methods=['POST'])
def handle_load_chapters():
    data = request.json
    comic_url = data.get('comic_url', '')
    adapter = data.get('adapter', 'biqu')
    crawler = Crawler(json_file)
    results = crawler.loadChapters(comic_url, adapter)
    return jsonify(results)

@app.route('/load_images', methods=['POST'])
def handle_load_images():
    data = request.json
    chapter_href = data.get('chapter_href', '')
    adapter = data.get('adapter', 'biqu')
    crawler = Crawler(json_file)
    results = crawler.loadImages(chapter_href, adapter)
    return jsonify(results)

@app.route('/download_chapter', methods=['POST'])
def handle_download_images():
    try:
        data = request.json
        comic_name = data.get('comic_name', '')
        chapter_name = data.get('chapter_name', '')
        chapter_href = data.get('chapter_href', '')
        adapter = data.get('adapter', 'biqu')
        comic_base_path = os.path.join(app.static_folder, 'comics')
        os.makedirs(comic_base_path, exist_ok=True)
        crawler = Crawler(json_file)
        crawler.downloadChapter(comic_name, chapter_name,chapter_href, comic_base_path, adapter)
        return jsonify({'success': True, 'message': 'Download completed'})
    except Exception as e:
        logging.exception(e)
        return jsonify({'success': False, 'message': str(e)})
    
@app.route('/load_downloaded_comics', methods=['POST'])
def handle_load_downloaded_comics():
    try:
        comic_base_path = os.path.join(app.static_folder, 'comics')
        os.makedirs(comic_base_path, exist_ok=True)
        crawler = Crawler(json_file)
        comics = crawler.load_downloaded_comics(comic_base_path)
        return jsonify({'success': True, 'data': list(comics)})
    except Exception as e:
        logging.exception(e)
        return jsonify({'success': False, 'message': str(e)})

@app.route('/load_downloaded_chapters', methods=['POST'])
def handle_load_downloaded_chapters():
    try:
        comic_name = request.json.get('comic_name', '')
        comic_base_path = os.path.join(app.static_folder, 'comics')
        os.makedirs(comic_base_path, exist_ok=True)
        crawler = Crawler(json_file)
        chapters = crawler.load_downloaded_chapters(comic_base_path,comic_name)
        for chapter in chapters:
            chapter = chapter.strip()
        return jsonify({'success': True, 'data': list(chapters)})
    except Exception as e:
        logging.exception(e)
        return jsonify({'success': False,'message': str(e)})

@app.route('/load_downloaded_images', methods=['POST'])
def handle_load_downloaded_images():
    try:
        comic_name = request.json.get('comic_name', '')
        chapter_name = request.json.get('chapter_name', '')
        comic_base_path = os.path.join(app.static_folder, 'comics')
        os.makedirs(comic_base_path, exist_ok=True)
        crawler = Crawler(json_file)
        images = crawler.load_downloaded_images(comic_base_path, comic_name, chapter_name)
        return jsonify({'success': True, 'data': list(images)})
    except Exception as e:
        logging.exception(e)
        return jsonify({'success': False,'message': str(e)})

@app.route('/delete_comic', methods=['POST'])
def handle_delete_comic():
    try:
        data = request.json
        comic_name = data.get('comic_name', '')
        comic_base_path = os.path.join(app.static_folder, 'comics')
        os.makedirs(comic_base_path, exist_ok=True)
        crawler = Crawler(json_file)
        crawler.delete_comic(comic_base_path, comic_name)
        return jsonify({'success': True, 'message': 'Comic deleted successfully'})
    except Exception as e:
        logging.exception(e)
        return jsonify({'success': False, 'message': str(e)})

@app.route('/delete_chapter', methods=['POST'])
def handle_delete_chapter():
    try:
        data = request.json
        comic_name = data.get('comic_name', '')
        chapter_name = data.get('chapter_name', '')
        comic_base_path = os.path.join(app.static_folder, 'comics')
        os.makedirs(comic_base_path, exist_ok=True)
        crawler = Crawler(json_file)
        crawler.delete_chapter(comic_base_path, comic_name, chapter_name)
        return jsonify({'success': True, 'message': 'Chapter deleted successfully'})
    except Exception as e:
        logging.exception(e)
        return jsonify({'success': False, 'message': str(e)})


if __name__ == '__main__':
    clean_temp_directory()
    port = int(sys.argv[1])
    if len(sys.argv) > 2:
        json_file = sys.argv[2]
    else:
        json_file = os.path.join(os.path.dirname(__file__), 'sources.json')
    os.makedirs(app.static_folder, exist_ok=True)
    os.makedirs(os.path.join(app.static_folder, 'comics'), exist_ok=True)

    app.run(debug=False, port=port, host='127.0.0.1', threaded=True)
