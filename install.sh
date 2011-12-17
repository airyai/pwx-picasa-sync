#!/bin/sh
if [ ! -d /usr/local/bin/picasasync-0.1 ]; then
	mkdir -p /usr/local/bin/picasasync-0.1
fi
cp src/*.py /usr/local/bin/picasasync-0.1
cp picasasync /usr/local/bin/

chmod +x /usr/local/bin/picasasync-0.1/picasasync.py
chmod +x /usr/local/bin/picasasync

./build.py

