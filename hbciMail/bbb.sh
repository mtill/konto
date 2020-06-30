#!/bin/bash

tmpfile="bbb.cbx"
if [ -e "$tmpfile" ]; then
 rm $tmpfile
fi

pnfile="bnk.png"
fromdate="--fromdate=$(date --date='-59 days' '+%Y%m%d')"
if [ "$1" == "all" ]; then
  fromdate=""
fi

aqbanking-cli -P $pnfile request -b xxxxxxxx -a xxxxxxxx $fromdate -c $tmpfile --transactions
if [ $? -ne 0 ]; then
 rm $tmpfile
 exit 1
fi

