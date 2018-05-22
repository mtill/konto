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

                resulttitle = getSubject(amount + currency + ' ' + name + ' ' + (' '.join(titlelist)))
                resultadditional['csv'] = date.replace(';', '_') + '; ' + amount.replace(';', '_') + '; ' + currency.replace(';', '_') + '; ' + name.strip().replace(';', '_') + '; ' + (' '.join(titlelist)).strip().replace(';', '_') + ';'

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
    def __init__(self, thepath, filenamebase):
        self.thepath = thepath
        self.filenamebase = filenamebase

    def performAction(self, contentList):
        thefilename = self.filenamebase + time.strftime("-%Y-%m")

        kontomodel.doLock(thefilename=thefilename, thepath=self.thepath)
        with open(os.path.join(self.thepath, thefilename + '.list'), 'a') as thefile:
            for content in contentList:
                if 'csv' in content.additional:
                    theline = content.additional['csv']
                    thefile.write(theline + "\n")

        kontomodel.doUnlock(thefilename=thefilename, thepath=self.thepath)

