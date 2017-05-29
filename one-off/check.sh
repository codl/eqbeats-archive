#!/bin/bash

skip=""

cd /run/media/codl/media3/eqbeats/var-lib-eqbeats/tracks/

ls | while read f; do
    tid="${f%%.*}"
    if [[ $tid == $skip ]]; then
        continue
    fi
    skip=$tid
    if curl -fIs "https://eqbeats.org/track/${tid}"; then true; else
        echo "$tid" >> ~/deleted
        continue
    fi
    echo $tid
    [[ -f "$tid.opus" ]] || echo "$tid.opus" >> ~/missing
    [[ -f "$tid.m4a" ]] || echo "$tid.m4a" >> ~/missing
    [[ -f "$tid.mp3" ]] || echo "$tid.mp3" >> ~/missing
    [[ -f "$tid.ogg" ]] || echo "$tid.ogg" >> ~/missing
done
