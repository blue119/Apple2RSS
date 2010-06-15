#!/bin/sh

cd ~/iLab/Apple2RSS
python apple2rss.py
python -m SimpleHTTPServer &
java -jar ~/iSoftware/sunrise-0.42j/sunrisecl.jar -maxupdates 2 apple_new.sdl
kill -9 `ps aux | grep SimpleHTTPServer | grep python | awk '{print $2}'`
rm -rf *.html

