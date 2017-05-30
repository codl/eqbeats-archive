from flask import Flask, request, redirect, Response
from werkzeug.datastructures import Headers
import boto3
from botocore.exceptions import ClientError
from io import BytesIO
from PIL import Image
import threading

app = Flask("eqbeats-archive")

s3 = boto3.resource('s3')
s3client = boto3.client('s3')

BUCKET = "eqbeats-archive"
BUCKET_DYN = "eqbeats-dynamic"

bucket = s3.Bucket(BUCKET)
bucket_dyn = s3.Bucket(BUCKET_DYN)

def url_format_to_extension(format):
    if format == "mp3":
        return "mp3"
    elif format == "aac":
        return "m4a"
    elif format == "vorbis":
        return "ogg"
    else:
        return "opus"

def s3_proxy(key, bucket=bucket.name, headers={}):
    obj = s3.Object(bucket, key)
    try:
        resp = obj.get(Range=request.headers.get("range", ""))
        def stream():
            yield b""
            buf = resp['Body'].read(1024)
            while buf:
                yield buf
                buf = resp['Body'].read(1024)

        status = 200

        full_headers = Headers()
        full_headers.set('content-length', resp['ContentLength'])
        full_headers.set('content-type', resp['ContentType'])
        full_headers.set('cache-control', 'max-age=43200')
        full_headers.set('accept-ranges', resp['AcceptRanges'])
        if 'ContentRange' in resp:
            full_headers.set('content-range', resp['ContentRange'])
            status = 206
        full_headers.set('etag', resp['ETag'])

        for key in headers:
            full_headers.set(key, headers[key])

        return Response(stream(), status, headers=full_headers)
    except ClientError as e:
        return Response(
                e.response['Error']['Code'],
                e.response['ResponseMetadata']['HTTPStatusCode'])

@app.route("/track/<tid>/mp3")
@app.route("/track/<tid>/aac")
@app.route("/track/<tid>/vorbis")
@app.route("/track/<tid>/opus")
def download(tid):
    format = request.path.split("/")[-1]
    ext = url_format_to_extension(format)

    return s3_proxy("tracks/%s.%s" % (tid, ext),
            headers={"content-disposition": "attachment"})

@app.route("/track/<tid>/original")
def download_original(tid):
    objects = list(bucket.objects.filter(Prefix="tracks/%s.orig" % (tid,)))
    if(len(objects) > 0):
        filename = objects[0].key
        return s3_proxy(filename)
    else:
        return s3_proxy("tracks/%s.mp3" %(tid,))

@app.route("/track/<tid>/art")
def download_art(tid):
    return s3_proxy("art/%s" % (tid,))

@app.route("/track/<tid>/art/thumb")
@app.route("/track/<tid>/art/medium")
def thumbnail(tid):
    type = request.path.split("/")[-1]
    dyn_key = "%s/%s" % (type, tid)
    try:
        obj = bucket_dyn.Object(dyn_key)
        obj.load()
        return s3_proxy(dyn_key, BUCKET_DYN,
                headers={"content-type": "image/jpeg"}
        )
    except ClientError as _:
        try:
            obj = bucket.Object("art/" + tid).get()
            objio = BytesIO(obj['Body'].read())
            image = Image.open(objio)
            image = image.convert("RGB")
            image.thumbnail(
                (1000,1000) if type == "medium"
                else (128, 64)
            )
            outio = BytesIO()
            image.save(outio, "jpeg", quality=93, progressive=True)
            outio.seek(0)
            outcopy = BytesIO(outio.getvalue())
            def upload():
                bucket_dyn.Object(dyn_key).put(Body=outio.getvalue(), ContentType="image/jpeg")
            threading.Thread(target=upload).run()
            return Response(outio.read(), 200, mimetype="image/jpeg")

        except ClientError as _:
            pass
    return download_art(tid)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def fallback_to_main_domain(path):
    return redirect("https://www.eqbeats.org" + request.full_path, code=307)
