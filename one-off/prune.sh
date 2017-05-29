#!/bin/bash

cd /run/media/codl/media3/eqbeats/var-lib-eqbeats/tracks/

cat ~/deleted | while read tid; do
    ls ${tid}.* | while read f; do
        aws s3 rm s3://eqbeats-archive/tracks/${f}
        rm -v "${f}"
    done
done
