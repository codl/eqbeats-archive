#!/bin/bash

cd /run/media/codl/media3/eqbeats/var-lib-eqbeats/tracks/

ls *.m4a | while read f; do
    tid=${f%%.*}
    echo $tid
    aws s3 cp --acl public-read --content-type video/mp4 --metadata-directive REPLACE s3://eqbeats-archive/tracks/$tid.m4a s3://eqbeats-archive/tracks/$tid.m4a
done
