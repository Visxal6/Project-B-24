import os
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
# ensure project root on path
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import django
django.setup()
from django.conf import settings
import boto3

bucket = os.environ.get('AWS_STORAGE_BUCKET_NAME')
if not bucket:
    raise SystemExit('AWS_STORAGE_BUCKET_NAME not set in environment')

media_root = settings.MEDIA_ROOT
prefix = getattr(settings, 'AWS_MEDIA_LOCATION', 'media')

print('Uploading files from', media_root, 'to s3 bucket', bucket, 'prefix', prefix)
client = boto3.client('s3')
count = 0
for root, dirs, files in os.walk(media_root):
    for fn in files:
        local_path = os.path.join(root, fn)
        rel_path = os.path.relpath(local_path, media_root)
        rel_path = rel_path.replace(os.sep, '/')
        s3_key = f"{prefix}/{rel_path}"
        print('Uploading', local_path, '->', s3_key)
        try:
            # Upload without setting ACL since some buckets block ACLs
            client.upload_file(local_path, bucket, s3_key)
            count += 1
        except Exception as e:
            print('ERROR uploading', local_path, e)

print('Uploaded', count, 'files')
