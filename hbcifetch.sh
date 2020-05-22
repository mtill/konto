#!/bin/bash


tmpfile="/tmp/dkb.cbx"
pnfile="bnk.png"

if [ -e "$tmpfile" ]; then
 rm $tmpfile
fi

fromdate="--fromdate=$(date --date='-59 days' '+%Y%m%d')"
if [ "$1" == "all" ]; then
  fromdate=""
fi

aqbanking-cli -P $pnfile request -b <BLZ> -a <ACCOUNT> $fromdate -c $tmpfile --transactions
if [ $? -ne 0 ]; then
 rm "$tmpfile"
 exit 1
fi

if [ $? -eq 0 ]; then
  ./hbciimport.py
fi
rm "$tmpfile"
