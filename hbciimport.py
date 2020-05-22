#!/usr/bin/env python3
# coding=utf-8


import calendar
import kontomodel
import subprocess
import datetime
import csv
import io
import sys


def fetchHBCI(k, requests):
    for therequest in requests:
        therequest["importedEntries"] = []
        # run command and retrieve output
        process = subprocess.Popen(therequest["command"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, close_fds=True)
        thefile = process.stdout
        content = thefile.read().decode(therequest.get("encoding", "utf-8"), errors='ignore')
        thefile.close()

        if process.wait() != 0:
            raise Exception("process terminated with an error: " + str(process.stderr) + "\n" + content)


        tt = csv.DictReader(io.StringIO(content), delimiter=";")
        for t in tt:
            if t["type"] == "notedStatement":
                continue
            if t["value_currency"].lower() == "eur":
                t["value_currency"] = ""
            e = {"date": datetime.datetime.strptime(t["valutaDate"], therequest["dateFormat"]).strftime("%d.%m.%Y"),
                 "name": t["remoteName"],
                 "description": t["purpose"],
                 "amount": float(t["value_value"]),
                 "account": therequest["account"],
                 "currency": t["value_currency"],
                 "category": None,
                 "note": None
                }
            checkDuplicateEntry = {
                "date": e["date"],
                "account": e["account"],
                "name": e["name"],
                "description": e["description"],
                "amount": e["amount"]
            }
            hasEntry = k.hasTransactionEntry(entry=checkDuplicateEntry)
            if not hasEntry:
                print()
                print("[" + e["date"] + "] " + ("{:10.2f}".format(e["amount"])) + e["currency"] + " " + e["name"] + ": " + e["description"] + " (" + e["account"] + ")")
                k.createTransactionEntry(entry=e)
                therequest["importedEntries"].append(e)


if __name__ == "__main__":
    print("=======================")
    k = kontomodel.KontoModel(sqlitefile='konto.sqlite')
    requests = []
    requests.append({
        "account": "dkb",
        "command": 'aqbanking-cli export --exporter=csv --profile=full -c /tmp/dkb.cbx',
        "dateFormat": "%Y/%m/%d"
    })
    fetchHBCI(k=k, requests=requests)
