#!/bin/bash
# date 2020-07-24 09:06:18
# author calllivecn <c-all@qq.com>

set -e

CWD=$(pwd -P)
TMP=$(mktemp -d -p "$CWD")

DEPEND_CACHE="${CWD}/depend-cache"

if [ -d "$DEPEND_CACHE" ];then
	echo "使用depend-cache～"
	cp -rv "$DEPEND_CACHE"/* "$TMP"
else
	mkdir -v "${DEPEND_CACHE}"
	pip install --no-compile --target "$DEPEND_CACHE" -r backend/requirements.txt
	cp -rv "$DEPEND_CACHE"/* "$TMP"
fi

NAME="easywg"
EXT=".pyz"

clean(){
	echo "clean... ${TMP}"
	rm -rf "${TMP}"
	echo "done"
}

trap clean SIGINT SIGTERM EXIT ERR

cp -rv backend/* "$TMP"
cp -rv frontend/dist/ "${TMP}/web_root"

find "$TMP" -type d -name "__pycache__" -exec rm -rv "{}" "+"

shiv --site-packages "$TMP" --compressed -p '/usr/bin/python3 -sE' -o "${NAME}.pyz" -e "main:main"
