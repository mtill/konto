#!/bin/bash

thetmpfile="/tmp/transbbb.png"
pnfile="/opt/MailWebsiteChanges/bnk/bnk.png"

aqbanking-cli -n -P $pnfile request -b "blz" -a "kontonummer" -c $thetmpfile --transactions --balance 2> /dev/null
if [ $? -ne 0 ]; then
 if [ -f $thetmpfile ]; then
  rm $thetmpfile
 fi
 exit 1
fi

aqbanking-cli listtrans -b "blz" -a "kontonummer" -c $thetmpfile
if [ $? -ne 0 ]; then
 if [ -f $thetmpfile ]; then
  rm $thetmpfile
 fi
 exit 1
fi

rm $thetmpfile

