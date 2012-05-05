#!/bin/sh
cd ${HOME}/iLab/AppleNews
# python apple2html.py
source ~/.pythonbrew/etc/bashrc
pythonbrew use Python-2.7.2
python apple2html.py
