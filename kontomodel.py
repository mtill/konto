#!/usr/bin/env python3
# coding=utf-8

import os
import time
import datetime
import calendar
import re
import html
import sqlite3


class KontoModel:
    def __init__(self, sqlitefile):
        self.conn = sqlite3.connect(sqlitefile)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def close(self):
        self.conn.close()

    def findCategory(self, theitem, categories, unknownCategory='nicht kategorisiert'):
        for category in categories:
            if category['compiledPattern'].search(theitem[category['field']]):
                return category['category']
        return unknownCategory

    def writeCategories(self, categoriesString):
        # validating the input string
        parsedCategories = self._parseCategories(categoriesString.split('\n'))

        self.cursor.execute('DELETE FROM categories')
        self.cursor.execute('VACUUM')
        self.cursor.executemany('INSERT INTO categories (category,field,pattern) VALUES (:category,:field,:pattern)', parsedCategories)
        self.conn.commit()

    def parseCategories(self):
        result = []
        for i in self.cursor.execute('SELECT * FROM categories'):
            result.append({'category': i['category'],
                           'field': i['field'],
                           'pattern': i['pattern'],
                           'compiledPattern': re.compile(i['pattern'])
                          })
        return result

    def _parseCategories(self, f):
        result = []
        for line in f:
            line = line.strip()
            if len(line) == 0 or line[0] == '#':
                continue

            categoryEnd = line.find(';')
            fieldEnd = line.find(';', categoryEnd+1)
            thepattern = line[fieldEnd+1:]
            if categoryEnd == -1 or fieldEnd == -1:
                raise ValueError('cannot parse categories string')
            field = line[categoryEnd+1:fieldEnd]
            if field not in ['account', 'name', 'description', 'amount', 'currency', 'note']:
                raise ValueError('cannot parse categories string: unknown field ' + field)

            result.append({
               'category': line[0:categoryEnd],
               'field': field,
               'pattern': thepattern
               # 'compiledPattern': re.compile(thepattern),
               })

        return result

    def getCategoriesAsString(self):
        result = ''
        categories = self.parseCategories()
        for c in categories:
            result = result + c['category'] + ';' + c['field'] + ';' + c['pattern'] + '\n'
        return result

    def getTransactions(self, accounts, fromDate, toDate):
        result = []

        timestampsql = ''
        sqlparam = []
        hasParams = False
        if fromDate is not None:
            timestampsql = timestampsql + 'timestamp>=? AND '
            fromDateTimestamp = fromDate.timestamp()
            sqlparam.append(fromDateTimestamp)
            hasParams = True
        if toDate is not None:
            timestampsql = timestampsql + 'timestamp<=? AND '
            toDateTimestamp = toDate.timestamp()
            sqlparam.append(toDateTimestamp)
            hasParams = True

        accountsql = ''
        if accounts is not None:
            sqlparam.extend(accounts)
            q = ','.join('?' * len(accounts))
            accountsql = 'account IN (' + q + ')'
            hasParams = True

        sqlquery = None
        if hasParams:
            sqlquery = self.cursor.execute('SELECT * FROM transactions WHERE ' + timestampsql + accountsql, sqlparam)
        else:
            sqlquery = self.cursor.execute('SELECT * FROM transactions')
        for c in sqlquery:
            if c['currency'] != '€':
                raise Exception('unknown currency ' + c['currency'])

            thecategory = '' if c['category'] is None else c['category']
            thenote = '' if c['note'] is None else c['note']
            dt = datetime.datetime.fromtimestamp(c['timestamp'])
            ctimestamp = calendar.timegm(dt.utctimetuple())
            result.append({'id': c['id'],
                    'timestamp': ctimestamp,
                    'account': c['account'],
                    'amount': float(c['amount']),
                    'currency': c['currency'],
                    'name': c['name'],
                    'description': c['description'],
                    'category': thecategory,
                    'note': thenote})

        return result

    # returns newly added item
    def addItem(self, thedate, theaccount, theamount, thecurrency, thename, thedescription, thecategory, thenote):
        timestamp = calendar.timegm(datetime.datetime.strptime(thedate, '%Y-%m-%d').utctimetuple())

        self.cursor.execute('INSERT INTO transactions (account,timestamp,amount,currency,name,description,category,note,id) VALUES (?,?,?,?,?,?,?,?,NULL)', (theaccount, timestamp, theamount, thecurrency, thename, thedescription, thecategory, thenote))
        theid = self.cursor.execute('SELECT last_insert_rowid()').fetchone()[0]
        self.conn.commit()

        result = {'id': theid,
                'timestamp': timestamp,
                'account': theaccount,
                'amount': theamount,
                'currency': thecurrency,
                'name': thename,
                'description': thedescription,
                'category': thecategory,
                'note': thenote}

        return result

    def getAccounts(self):
        q = self.cursor.execute('SELECT DISTINCT account FROM transactions ORDER BY account ASC')
        result = q.fetchall()
        return [i[0] for i in result]

    def getConsolidated(self, byCategory, traceNames, fromDate, toDate, categories, accounts, thepattern=None, categorySelection=None, sortScatterBy='timestamp', legendonlyTraces=None):
        filecontent = self.getTransactions(accounts=accounts, fromDate=fromDate, toDate=toDate)
        duplicatesMap = {}
        foundDuplicates = []

        allcategoriesNames = []
        for c in categories:
            if c['category'] not in allcategoriesNames:
                allcategoriesNames.append(c['category'])

        scatterlist = []
        allcategories = {}
        sumdict = {}
        incomedict = {}

        compiledPattern = None
        if thepattern is not None:
            compiledPattern = re.compile(thepattern, re.IGNORECASE)

        for f in filecontent:
            if len(f['category']) == 0:
                dupLine = str(f['timestamp']) + ' ' + str(f['amount']) + ' ' + f['currency'] + ' ' + f['name'] + ' ' + f['description']
                if dupLine in duplicatesMap:
                    foundDuplicates.append(html.escape(dupLine))
                else:
                    duplicatesMap[dupLine] = True
                f['category'] = self.findCategory(theitem=f, categories=categories)
            else:
                if f['category'] not in allcategoriesNames:
                    allcategoriesNames.append(f['category'])

            if (categorySelection is None or f['category'] in categorySelection)\
                and (compiledPattern is None or compiledPattern.search('|'.join(map(str, f.values())))):

                thedate = datetime.datetime.fromtimestamp(f['timestamp'])
                theX = thedate.strftime('%Y-%m-%d')

                if byCategory == 'month' or byCategory == 'profit':
                    theX = theX[0:7]
                elif byCategory == 'year':
                    theX = theX[0:4]

                f['theX'] = theX
                scatterlist.append(f)

                if theX not in sumdict:
                    sumdict[theX] = 0
                sumdict[theX] += f['amount']

                if f['category'] not in allcategories:
                    allcategories[f['category']] = {}
                xy = f['amount']
                if theX in allcategories[f['category']]:
                    xy = xy + allcategories[f['category']][theX]
                allcategories[f['category']][theX] = xy
                if xy > 0:
                    if theX not in incomedict:
                        incomedict[theX] = 0
                    incomedict[theX] += f['amount']

        traces = []
        if 'profit' in traceNames:
            profit = {'x': [], 'y': [], 'name': 'Gewinn', 'type': 'scatter', 'line': {'color': 'red', 'dash': 'dot'}}
            for key in sorted(sumdict.keys()):
                profit['x'].append(key)
                profit['y'].append(sumdict[key])
            traces.append(profit)

        if 'totalprofit' in traceNames:
            totalprofit = {'x': [], 'y': [], 'name': 'Gewinn aufsummiert', 'type': 'scatter', 'line': {'dash': 'dot'}}
            totalsum = 0
            for key in sorted(sumdict.keys()):
                totalprofit['x'].append(key)
                totalsum = totalsum + sumdict[key]
                totalprofit['y'].append(totalsum)
            traces.append(totalprofit)

        if 'income' in traceNames:
            income = {'x': [], 'y': [], 'name': 'Einkommen', 'type': 'scatter'}
            for key in sorted(incomedict.keys()):
                income['x'].append(key)
                income['y'].append(incomedict[key])
            traces.append(income);

        if 'traces' in traceNames:
            for key in sorted(allcategories.keys(), key=lambda x: x.lower()):
                thetrace = {'x': [],
                            'y': [],
                            'name': key,
                            'type': 'bar'}
                if legendonlyTraces is not None and key in legendonlyTraces:
                    thetrace["visible"] = "legendonly"
                for tracekey in sorted(allcategories[key].keys()):
                    thetrace['x'].append(tracekey)
                    thetrace['y'].append(allcategories[key][tracekey])
                traces.append(thetrace)

        result = {'traces': traces, 'foundDuplicates': foundDuplicates}
        if 'scatter' in traceNames:
            scatter = {'timestamp': [], 'account': [], 'id': [], 'amount': [], 'category': [], 'currency': [], 'name': [], 'description': [], 'note': [], 'theX': []}
            # 'mode': 'markers', 'type': 'scatter', 'visible': 'legendonly', 'name': 'Einzelumsätze', 'text': [], 'marker': {'size': 5, 'opacity': 0.5}
            scatterlist = sorted(scatterlist, key=lambda x: x[sortScatterBy])
            for x in scatterlist:
                scatter['timestamp'].append(x['timestamp'])
                scatter['account'].append(x['account'])
                scatter['id'].append(x['id'])
                scatter['amount'].append(x['amount'])
                scatter['currency'].append(x['currency'])
                scatter['category'].append(x['category'])
                # scatter['text'].append(x['name'] + ' ' + x['title'])
                scatter['name'].append(x['name'])
                scatter['description'].append(x['description'])
                scatter['note'].append(x['note'])
                scatter['theX'].append(x['theX'])
            result['scatter'] = scatter

        result['allcategoriesNames'] = sorted(allcategoriesNames, key=lambda x: x.lower())
        return result

    def updateItem(self, itemId, theaccount=None, thename=None, thedescription=None, theamount=None, thecurrency=None, thecategory=None, thenote=None):
        sqlparts = []
        sqlparams = []
        if theaccount is not None:
            sqlparts.append('account=?')
            sqlparams.append(theaccount)
        if thename is not None:
            sqlparts.append('name=?')
            sqlparams.append(thename)
        if thedescription is not None:
            sqlparts.append('description=?')
            sqlparams.append(thedescription)
        if theamount is not None:
            sqlparts.append('amount=?')
            sqlparams.append(theamount)
        if thecurrency is not None:
            sqlparts.append('currency=?')
            sqlparams.append(thecurrency)
        if thecategory is not None:
            sqlparts.append('category=?')
            sqlparams.append(thecategory)
        if thenote is not None:
            sqlparts.append('note=?')
            sqlparams.append(thenote)

        if len(sqlparams) == 0:
            return False
        sqlparams.append(itemId)

        self.cursor.execute('UPDATE transactions SET ' + (','.join(sqlparts)) + ' WHERE id=?', sqlparams)
        self.conn.commit()
        return True

    def deleteItem(self, itemId):
        self.cursor.execute('DELETE FROM transactions WHERE id=?', [itemId])
        self.conn.commit()

    def convertToItem(self, scatter, pos):
        return {
            'date': scatter['date'][i],
            'account': scatter['account'][i],
            'amount': scatter['amount'][i],
            'currency': scatter['currency'][i],
            'name': scatter['name'][i],
            'description': scatter['description'][i],
            'category': scatter['category'][i],
            'note': scatter['note'][i],
            'id': scatter['id'][i]
        }

    def getUncategorizedItems(self, fromDate=None, toDate=None, accounts=None, legendonlyTraces=None):
        categories = self.parseCategories()
        consolidated = self.getConsolidated(byCategory='month', traceNames=['scatter'], fromDate=fromDate, toDate=None, categories=categories, accounts=accounts, legendonlyTraces=legendonlyTraces)
        scatter = consolidated['scatter']

        result = {}
        result['allcategoriesNames'] = consolidated['allcategoriesNames']
        resultItems = {'timestamp': [], 'account': [], 'id': [], 'amount': [], 'category': [], 'currency': [], 'name': [], 'description': [], 'note': [], 'theX': []}
        for i in range(0, len(scatter['timestamp'])):
            if scatter['category'][i] == '' or scatter['category'][i] == 'nicht kategorisiert':
                resultItems['timestamp'].append(scatter['timestamp'][i])
                resultItems['account'].append(scatter['account'][i])
                resultItems['id'].append(scatter['id'][i])
                resultItems['amount'].append(scatter['amount'][i])
                resultItems['currency'].append(scatter['currency'][i])
                resultItems['name'].append(scatter['name'][i])
                resultItems['description'].append(scatter['description'][i])
                resultItems['category'].append(scatter['category'][i])
                resultItems['note'].append(scatter['note'][i])
                resultItems['theX'].append(scatter['theX'][i])
        result['items'] = resultItems
        return result


if __name__ == "__main__":
    m = KontoModel('konto.sqlite')
    #t = m.getTransactions()
    #print(t)

    #id = m.appendItem(1234, 'theaccount', 3.3, '$', 'test', 'descr', 'category', 'note')
    #u = m.getUncategorizedItems(accounts=['dkb'])
    u = m.getUncategorizedItems(fromDate='2018-01-01', toDate='2018-01-03', accounts=['bbb'])
    for i in u:
        print(i['id'])
    m.close()
