from flask import Flask, request, redirect, Response
import boto3
from botocore.exceptions import ClientError
from io import BytesIO
from PIL import Image

app = Flask("eqbeats-archive")

s3 = boto3.resource('s3')
s3client = boto3.client('s3')

BUCKET = "eqbeats-archive"

bucket = s3.Bucket(BUCKET)

def url_format_to_extension(format):
    if format == "mp3":
        return "mp3"
    elif format == "aac":
        return "m4a"
    elif format == "vorbis":
        return "ogg"
    else:
        return "opus"

def redir_to_s3(filename, attachment=False):
    params = {
            'Bucket': BUCKET,
            'Key': filename,
            'ResponseContentDisposition': 'attachment' if attachment else 'inline',
            'ResponseCacheControl': 'max-age=31557600'
    }
    url = s3client.generate_presigned_url(ClientMethod='get_object', Params=params)

    return redirect(url)


@app.route("/track/<tid>/mp3")
@app.route("/track/<tid>/aac")
@app.route("/track/<tid>/vorbis")
@app.route("/track/<tid>/opus")
def download(tid):
    format = request.path.split("/")[-1]
    ext = url_format_to_extension(format)

    return redir_to_s3("tracks/%s.%s" % (tid, ext), attachment=True)

@app.route("/track/<tid>/original")
def download_original(tid):
    objects = list(bucket.objects.filter(Prefix="tracks/%s.orig" % (tid,)))
    if(len(objects) > 0):
        filename = objects[0].key
        return redir_to_s3(filename)
    else:
        return redir_to_s3("tracks/%s.mp3" %(tid,))

@app.route("/track/<tid>/art")
def download_art(tid):
    return redir_to_s3("art/%s" % (tid,))

@app.route("/track/<tid>/art/thumb")
@app.route("/track/<tid>/art/medium")
def thumbnail(tid):
    type = request.path.split("/")[-1]
    try:
        obj = bucket.Object("art/" + tid).get()
        objio = BytesIO(obj['Body'].read())
        image = Image.open(objio)
        image.thumbnail(
            (1000,1000) if type == "medium"
            else (128, 64)
        )
        outio = BytesIO()
        image.save(outio, "jpeg", quality=93, progressive=True)
        outio.seek(0)
        return Response(outio.read(), 200, mimetype="image/jpeg")

    except ClientError as _:
        pass
    return download_art(tid)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def fallback_to_main_domain(path):
    return redirect("https://www.eqbeats.org" + request.full_path, code=307)
