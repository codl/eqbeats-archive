#!/bin/bash

cd /run/media/codl/media3/eqbeats/var-lib-eqbeats/tracks/

cat ~/missing | while read f; do
    tid=${f%%.*}
    ext=${f##*.}
    echo $tid $ext
    case $ext in
        mp3)
            codec=mp3
            ;;
        m4a)
            codec=aac
            ;;
        opus)
            codec=libopus
            ;;
        ogg)
            codec=libvorbis
            ;;
    esac
    ffmpeg -nostdin -i $tid.orig.* -vn -c:a $codec "$f"
done

