#!/usr/bin/env python3
# coding=utf-8

import sys
kontodir = '/home/pi/konto'
sys.path.append(kontodir)
import kontomodel

from mwctools import URLReceiver as uri
from mwctools import CommandReceiver as command
from mwctools import XPathParser as xpath
from mwctools import CSSParser as css
from mwctools import RegExParser as regex
from mwctools import Content
from mwctools import Parser
from mwctools import getSubject

import os.path
import csv
import time


class HBCIParser(Parser):
    # input: [Content], output: [Content]
    def performAction(self, contentList):
        result = []
        for content in contentList:
            result.append(self.parseOneObject(content))
        return result

    # input: content, output: content
    def parseOneObject(self, content):
        contentsplits = csv.reader([content.content], delimiter=';')

        resulttitle = content.title
        resultcontent = content.content
        resultadditional = {} if content.additional is None else content.additional.copy()

        for contentsplit in contentsplits:
            if len(contentsplit) == 32:
                date = contentsplit[6]
                currency = (' ' + contentsplit[8]).replace(' EUR', '€')
                amount = contentsplit[7]
                name = contentsplit[10]+contentsplit[11]
                titlelist = contentsplit[12:22]

                # addItem(self, thedate, theaccount, theamount, thecurrency, thename, thedescription, thecategory, thenote)
                resulttitle = getSubject(amount + currency + ' ' + name + ' ' + (' '.join(titlelist)))
                if not content.content.startswith("\"transactionId\";\"localBankCode\";"):
                    resultadditional['csv'] = {'thedate': date.replace('/', '-'),
                                               'theamount': float(amount),
                                               'thecurrency': currency,
                                               'thename': name.strip(),
                                               'thedescription': (' '.join(titlelist)).strip()
                                              }

                resultcontent = 'Date: ' + date + '<br>\nName: ' + name + '<br>\nAmount: ' + amount + currency + '<br><br>Details:<br>\n' + ('\n<br>'.join(titlelist))
            break

        return Content(uri=content.uri, encoding=content.encoding, title=resulttitle, content=resultcontent, contenttype='html', additional=resultadditional)


class HBCIBalanceParser(Parser):
    # input: [Content], output: [Content]
    def performAction(self, contentList):
        result = []
        for content in contentList:
            result.append(self.parseOneObject(content))
        return result

    # input: content, output: content
    def parseOneObject(self, content):
        thesplit = content.content.split("\t")
        resulttitle = "Kontostand " + ": " + thesplit[7] + " " + thesplit[8]
        resultcontent = resulttitle
        resultadditional = content.additional

        return Content(uri=content.uri, encoding=content.encoding, title=resulttitle, content=resultcontent, contenttype='html', additional=resultadditional)


class SaveTitlesParser(Parser):
    def __init__(self, sqlitefile, account):
        self.sqlitefile = sqlitefile
        self.account = account

    def performAction(self, contentList):
        print(self.sqlitefile)
        k = kontomodel.KontoModel(sqlitefile=self.sqlitefile)
        for content in contentList:
            if 'csv' in content.additional:
                i = content.additional['csv']
                k.addItem(thedate=i['thedate'], theaccount=self.account, theamount=i['theamount'], thecurrency=i['thecurrency'], thename=i['thename'], thedescription=i['thedescription'], thecategory=None, thenote=None)

