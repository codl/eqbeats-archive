from flask import Flask, request, redirect
import boto3

app = Flask("eqbeats-archive")

s3 = boto3.client('s3')

def url_format_to_extension(format):
    if format == "mp3":
        return "mp3"
    elif format == "aac":
        return "m4a"
    elif format == "vorbis":
        return "ogg"
    else:
        return "opus"

#@app.route("/track/<id>/original")
@app.route("/track/<tid>/mp3")
@app.route("/track/<tid>/aac")
@app.route("/track/<tid>/vorbis")
@app.route("/track/<tid>/opus")
def download(tid):
    format = request.path.split("/")[-1]
    ext = url_format_to_extension(format)

    bucket = "eqbeats-archive"
    key = "tracks/%s.%s" % (tid, ext)

    url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params= { 'Bucket': bucket, 'Key': key }
        )

    return redirect(url)
