from PIL import Image
import boto3
from io import BytesIO
import mimetypes

SOURCE_BUCKET="eqbeats-archive"
SOURCE_PREFIX="art/"
DEST_BUCKET="eqbeats-archive"
DEST_PREFIX="art/"

mimetypes.add_type("image/vnd.adobe.photoshop", ".psd")

s3 = boto3.resource('s3')

source = s3.Bucket(SOURCE_BUCKET)
dest = s3.Bucket(DEST_BUCKET)

def get_mime(key):
    f = BytesIO()
    source.download_fileobj(key, f)
    image = Image.open(f)
    mime, _ = mimetypes.guess_type("x." + image.format)
    if not mime:
        raise Exception("frick %s" % ( image.format, ))
    return mime

if __name__ == "__main__":
    problematic = []
    for obj in source.objects.filter(Prefix = SOURCE_PREFIX):
        try:
            print(obj.key)
            mime = get_mime(obj.key)
            print(mime)
            dest.copy(
                    {'Key' : obj.key, 'Bucket' : SOURCE_BUCKET},
                    DEST_PREFIX + obj.key[len(SOURCE_PREFIX):],
                    {'ContentType': mime, 'ACL': 'public-read', 'MetadataDirective': 'REPLACE'}
            )
        except Exception as e:
            print(e)
            problematic.append(obj.key)
    print("problems: %s", problematic)
