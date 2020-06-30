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
            #"localCountry";"localBankCode";"localBranchId";"localAccountNumber";"localSuffix";"localIban";"localName";"localBic";"remoteCountry";"remoteBankName";"remoteBankLocation";"remoteBankCode";"remoteBranchId";"remoteAccountNumber";"remoteSuffix";"remoteIban";"remoteName";"remoteName1";"remoteBic";"uniqueId";"idForApplication";"groupId";"valutaDate";"date";"value_value";"value_currency";"fees_value";"fees_currency";"textKey";"textKeyExt";"transactionKey";"customerReference";"bankReference";"transactionCode";"transactionText";"primanota";"fiId";"purpose";"purpose1";"purpose2";"purpose3";"purpose4";"purpose5";"purpose6";"purpose7";"purpose8";"purpose9";"purpose10";"purpose11";"category";"category1";"category2";"category3";"category4";"category5";"category6";"category7";"period";"cycle";"executionDay";"firstDate";"lastDate";"nextDate";"type";"subType";"status";"charge";"remoteAddrStreet";"remoteAddrZipcode";"remoteAddrCity";"remotePhone";"unitId";"unitIdNameSpace";"units_value";"units_currency";"unitPriceValue_value";"unitPriceValue_currency";"commissionValue_value";"commissionValue_currency";"bankAccountId";"groupId";"creditorSchemeId";"originatorId";"mandateId";"mandateDate";"mandateDebitorName";"sequence";"originalCreditorSchemeId";"originalMandateId";"originalCreditorName";"endToEndReference"
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
        "account": "bbb",
        "command": 'aqbanking-cli export --exporter=csv --profile=mwc-full -c /tmp/bbb.cbx',
        "dateFormat": "%Y/%m/%d"
    })
    fetchHBCI(k=k, requests=requests)

