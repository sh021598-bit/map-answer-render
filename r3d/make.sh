#!/bin/sh
# 사용: sh make.sh <영상설정.json> <작업폴더> [음성폴더]   → 작업폴더/out.mp4
# 작업폴더 준비물: models/(Kokoro), world50.json, node_modules(three·playwright·fontsource)
set -e; R=$(cd "$(dirname "$0")" && pwd); CFG=$(realpath "$1"); cd "$2"; mkdir -p data
cp "$R"/index.html "$R"/props.js "$R"/render.js . && cp "$CFG" data/config.json
python3 -I "$R"/prep3d.py data/config.json
python3 -I "$R"/audio3d.py data/config.json ${3:+$(realpath "$3")}
(python3 -m http.server 8765 >/dev/null 2>&1 &) ; sleep 1
node render.js out.mp4 30
