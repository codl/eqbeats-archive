from flask import Flask, request, redirect
import boto3

app = Flask("eqbeats-archive")

s3 = boto3.client('s3')

BUCKET = "eqbeats-archive"
KEY_PREFIX = ""

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
            'Key': KEY_PREFIX + filename,
            'ResponseContentDisposition': 'attachment' if attachment else 'inline',
            'ResponseCacheControl': 'max-age=31557600'
    }
    url = s3.generate_presigned_url(ClientMethod='get_object', Params=params)

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
    resp = s3.list_objects_v2(Bucket=BUCKET,
            Prefix="%stracks/%s.orig" % (KEY_PREFIX, tid))
    if(resp['KeyCount'] > 0):
        filename = resp['Contents'][0]['Key'].replace(KEY_PREFIX, "", 1)
        return redir_to_s3(filename)
    else:
        return redir_to_s3("tracks/%s.mp3" %(tid,))

@app.route("/track/<tid>/art")
def download_art(tid):
    return redir_to_s3("art/%s" % (tid,))

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def fallback_to_main_domain(path):
    return redirect("https://www.eqbeats.org" + request.full_path, code=307)
