import os
import sys
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
import django
django.setup()
from forum.models import Post
import requests

def fetch_page(url):
    try:
        r = requests.get(url, timeout=5)
        print(f'PAGE {url} status:', r.status_code)
        snippet = r.text[:1000].split('\n')
        print('HTML snippet (first 20 lines):')
        for line in snippet[:20]:
            print(line)
    except Exception as e:
        print('Error fetching page', url, e)


fetch_page('http://127.0.0.1:8000/forum/')

for p in Post.objects.all():
    url = p.image.url
    try:
        ri = requests.get(url, timeout=5)
        print('Image URL:', url)
        print('  status:', ri.status_code)
        print('  content-type:', ri.headers.get('Content-Type'))
        print('  content-length:', ri.headers.get('Content-Length'))
    except Exception as e:
        print('  Error requesting image URL:', e)
