import os
import sys
# Ensure project root is on sys.path so 'main' settings package can be imported
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
os.environ.setdefault('DJANGO_SETTINGS_MODULE','main.settings')
import django
django.setup()
from forum.models import Post
from django.conf import settings
print('MEDIA_URL=', settings.MEDIA_URL)
posts = list(Post.objects.all())
print('Post count:', len(posts))
for p in posts:
    print('Post', p.id, 'image.name=', getattr(p.image, 'name', None))
    try:
        print('  url=', p.image.url)
    except Exception as e:
        print('  url error:', type(e).__name__, e)

# Try listing S3 objects under media/ using boto3
try:
    import boto3
    bucket = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    if not bucket:
        print('No AWS_STORAGE_BUCKET_NAME in env')
    else:
        s3 = boto3.client('s3')
        resp = s3.list_objects_v2(Bucket=bucket, Prefix='media/')
        print('S3 objects (media/):', resp.get('KeyCount',0))
        if 'Contents' in resp:
            for o in resp['Contents'][:50]:
                print(' -', o['Key'], o.get('Size'))
except Exception as e:
    print('boto3 error:', type(e).__name__, e)
