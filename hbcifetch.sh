#!/bin/bash


allparam=""
if [ "$1" == "all" ]; then
  allparam="all"
fi
set -o pipefail


/home/pi/konto/hbciMail/bbb.sh $allparam
if [ $? -eq 0 ]; then
  /home/pi/konto/hbciimport.py
fi
rm /tmp/bbb.cbx
