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
        isExistingDB = os.path.exists(sqlitefile)

        self.conn = sqlite3.connect(sqlitefile)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

        if not isExistingDB:
            with open('dbmodel.sql', 'r') as thefile:
                self.conn.executescript(thefile.read())
            print("initiated new database")

    def close(self):
        self.conn.close()

    def findCategory(self, theitem, categories, unknownCategory='not categorized'):
        for category in categories:
            if category['compiledPattern'].search(theitem[category['field']]):
                return category['category']
        return unknownCategory

    def getCategoriesNames(self):
        result = []
        for i in self.cursor.execute('SELECT DISTINCT category FROM categories ORDER BY category ASC'):
            result.append(i['category'])
        return result

    def parseCategories(self):
        result = []
        for i in self.cursor.execute('SELECT rowid,* FROM categories'):
            result.append({'id': i["rowid"],
                           'category': i['category'],
                           'field': i['field'],
                           'pattern': i['pattern'],
                           'compiledPattern': re.compile(i['pattern']),
                           'expectedValue': None if i['expectedValue'] is None or i['expectedValue'] == 'None' or len(str(i['expectedValue']).strip()) == 0 else float(i['expectedValue']),
                           "priority": i['priority']
                          })
        return result

    def getTransactions(self, accounts, fromDate, toDate, minAmount, maxAmount, categorySelection=None, thepattern=None):
        result = []

        compiledPattern = None
        if thepattern is not None:
            compiledPattern = re.compile(thepattern, re.IGNORECASE)
        duplicatesMap = {}

        allcategoriesNames = []
        categories = self.parseCategories()
        for cc in categories:
            if cc['category'] not in allcategoriesNames:
                allcategoriesNames.append(cc['category'])

        sqlparts = []
        sqlparam = []

        if fromDate is not None:
            sqlparts.append('timestamp>=?')
            fromDateTimestamp = calendar.timegm(fromDate.utctimetuple())
            sqlparam.append(fromDateTimestamp)
        if toDate is not None:
            sqlparts.append('timestamp<=?')
            toDateTimestamp = calendar.timegm(toDate.utctimetuple())
            sqlparam.append(toDateTimestamp)

        if minAmount is not None:
            sqlparts.append('amount>=?')
            sqlparam.append(minAmount)
        if maxAmount is not None:
            sqlparts.append('amount<=?')
            sqlparam.append(maxAmount)

        if accounts is not None:
            sqlparam.extend(accounts)
            q = ','.join('?' * len(accounts))
            sqlparts.append('account IN (' + q + ')')

        sqlquery = None
        if len(sqlparts) != 0:
            sqlquery = self.cursor.execute('SELECT rowid,* FROM transactions WHERE ' + (' AND '.join(sqlparts)), sqlparam)
        else:
            sqlquery = self.cursor.execute('SELECT rowid,* FROM transactions')

        for c in sqlquery:
            if c['currency'] != '€' and c["currency"] != "EUR" and c["currency"] != "":
                raise Exception('unknown currency ' + c['currency'])

            thecategory = c['category']
            if thecategory is None or len(thecategory) == 0:
                thecategory = self.findCategory(theitem=c, categories=categories)
            else:
                if thecategory not in allcategoriesNames:
                    allcategoriesNames.append(thecategory)

            notestr = ""
            if c['note'] is not None:
                notestr = c['note']
            dupLine = str(c['timestamp']) + ' ' + str(c['amount']) + ' ' + c['name'] + ' ' + notestr
            if dupLine not in duplicatesMap:
                duplicatesMap[dupLine] = []
            duplicatesMap[dupLine].append({"date":          datetime.datetime.fromtimestamp(c["timestamp"]).strftime("%Y-%m-%d"),
                                           "id":            c["rowid"],
                                           "name":          c["name"],
                                           "description":   c["description"],
                                           "amount":        "{:.2f}".format(c["amount"]),
                                           "amountint":     c["amount"],
                                           "currency":      c["currency"],
                                           "note":          c["note"]})

            if thecategory is None:
                thecategory = ''
            thenote = '' if c['note'] is None else c['note']
            e = {'id': c['rowid'],
                 'timestamp': c['timestamp'],
                 'account': c['account'],
                 'amount': float(c['amount']),
                 'currency': c['currency'],
                 'name': c['name'],
                 'description': c['description'],
                 'category': thecategory,
                 'note': thenote}
            if (categorySelection is None or thecategory in categorySelection)\
                and (compiledPattern is None or compiledPattern.search('|'.join(map(str, e.values())))):
                result.append(e)

        foundDuplicates = []
        for k, v in duplicatesMap.items():
            if len(v) > 1:
                foundDuplicates.extend(v)
        return {"transactions": result, "foundDuplicates": foundDuplicates, "allcategoriesNames": sorted(allcategoriesNames, key=lambda x: x.lower())}

    def createTransactionEntry(self, entry):
        if len(entry) == 0:
            return None

        thetimestamp = calendar.timegm(datetime.datetime.strptime(entry["date"], '%d.%m.%Y').utctimetuple())
        self.cursor.execute('INSERT INTO transactions (account,timestamp,amount,currency,name,description,category,note) VALUES (?,?,?,?,?,?,?,?)',
            [entry["account"], thetimestamp, entry["amount"], entry["currency"], entry["name"], entry["description"], entry["category"], entry["note"]])
        theid = self.cursor.execute('SELECT last_insert_rowid()').fetchone()[0]
        self.conn.commit()

        return theid

    def createCategoryEntry(self, entry):
        ev = None
        if len(entry["expectedValue"].strip()) != 0:
            ev = float(entry["expectedValue"])
        self.cursor.execute('INSERT INTO categories (category,field,pattern,expectedValue,priority) VALUES (?,?,?,?,?)',
            [entry["category"], entry["field"], entry["pattern"], ev, entry["priority"]])
        theid = self.cursor.execute('SELECT last_insert_rowid()').fetchone()[0]
        self.conn.commit()

        return theid

    def getAccounts(self):
        q = self.cursor.execute('SELECT DISTINCT account FROM transactions ORDER BY account ASC')
        result = q.fetchall()
        return [i[0] for i in result]

    def _buildTrace(self, thetrace, key, dateValueDict, legendonlyTraces):
        if legendonlyTraces is not None and key in legendonlyTraces:
            thetrace["visible"] = "legendonly"
        for tracekey in sorted(dateValueDict.keys()):
            thetrace['x'].append(tracekey)
            thetrace['y'].append(dateValueDict[tracekey])

    def _buildSumTrace(self, thetrace, key, dateValueDict, legendonlyTraces):
        if legendonlyTraces is not None and key in legendonlyTraces:
            thetrace["visible"] = "legendonly"
        lastval = 0.0
        for tracekey in sorted(dateValueDict.keys()):
            thetrace['x'].append(tracekey)
            lastval = lastval + dateValueDict[tracekey]
            thetrace['y'].append(lastval)

    def getConsolidated(self, transactions, groupBy, traceNames, sortScatterBy='timestamp', sortScatterByReverse=False, legendonlyTraces=None):
        scatterlist = []
        sumdict = {}
        incomedict = {}
        keyMap = {"category": {},
                  "name": {}
                 }

        for f in transactions:
            thedate = datetime.datetime.fromtimestamp(f['timestamp'])

            theX = None
            if groupBy == 'week':
                theX = thedate.strftime('%G-week %V')
            elif groupBy == 'month':
                theX = thedate.strftime('%Y-%m')
            elif groupBy == 'quarter':
                theX = str(thedate.strftime('%Y')) + "-quarter " + str(((thedate.month-1)//3)+1)
            elif groupBy == 'year':
                theX = thedate.strftime('%Y')
            else:
                theX = thedate.strftime('%Y-%m-%d')

            f['theX'] = theX
            scatterlist.append(f)

            if theX not in sumdict:
                sumdict[theX] = 0.0
            sumdict[theX] += f['amount']

            for keyToMap in keyMap.keys():
                if keyToMap not in f:
                    break

                fkey = f[keyToMap]
                if fkey not in keyMap[keyToMap]:
                    keyMap[keyToMap][fkey] = {}
                xy = f['amount']
                if theX in keyMap[keyToMap][fkey]:
                    xy = xy + keyMap[keyToMap][fkey][theX]
                keyMap[keyToMap][fkey][theX] = xy


            if f['amount'] > 0:
                if theX not in incomedict:
                    incomedict[theX] = 0.0
                incomedict[theX] += f['amount']


        traces = {}
        if 'profit' in traceNames:
            profit = {'x': [], 'y': [], 'name': 'profit', 'type': 'scatter', 'line': {'color': 'red', 'dash': 'dot'}}
            self._buildTrace(thetrace=profit, key="profit", dateValueDict=sumdict, legendonlyTraces=legendonlyTraces)
            traces["profit"] = [profit]

        if 'profitaccumulated' in traceNames:
            profitaccumulated = {'x': [], 'y': [], 'name': 'profit (accumulated)', 'type': 'scatter', 'line': {'dash': 'dot'}}
            self._buildSumTrace(thetrace=profitaccumulated, key="profitaccumulated", dateValueDict=sumdict, legendonlyTraces=legendonlyTraces)
            traces["profitaccumulated"] = [profitaccumulated]

        if 'income' in traceNames:
            income = {'x': [], 'y': [], 'name': 'income', 'type': 'scatter'}
            self._buildTrace(thetrace=income, key="income", dateValueDict=incomedict, legendonlyTraces=legendonlyTraces)
            traces["income"] = [income]

        if 'incomeaccumulated' in traceNames:
            incomeaccumulated = {'x': [], 'y': [], 'name': 'income', 'type': 'scatter'}
            self._buildSumTrace(thetrace=incomeaccumulated, key="incomeaccumulated", dateValueDict=incomedict, legendonlyTraces=legendonlyTraces)
            traces["incomeaccumulated"] = [incomeaccumulated]

        if 'traces' in traceNames:
            tracesList = []
            for key in sorted(keyMap["category"].keys(), key=lambda x: x.lower()):
                thetrace = {'x': [], 'y': [], 'name': key, 'type': 'bar'}
                self._buildTrace(thetrace=thetrace, key=key, dateValueDict=keyMap["category"][key], legendonlyTraces=legendonlyTraces)
                tracesList.append(thetrace)
            traces["traces"] = tracesList

        if 'tracesaccumulated' in traceNames:
            tracesaccumulatedList = []
            for key in sorted(keyMap["category"].keys(), key=lambda x: x.lower()):
                thetrace = {'x': [], 'y': [], 'name': key + ' (accumulated)', 'type': 'scatter'}
                self._buildSumTrace(thetrace=thetrace, key=key, dateValueDict=keyMap["category"][key], legendonlyTraces=legendonlyTraces)
                tracesaccumulatedList.append(thetrace)
            traces["tracesaccumulated"] = tracesaccumulatedList

        if 'nametraces' in traceNames:
            nametracesList = []
            for key in sorted(keyMap["name"].keys(), key=lambda x: x.lower()):
                thetrace = {'x': [], 'y': [], 'name': key, 'type': 'bar'}
                self._buildTrace(thetrace=thetrace, key=key, dateValueDict=keyMap["name"][key], legendonlyTraces=legendonlyTraces)
                nametracesList.append(thetrace)
            traces["nametraces"] = nametracesList

        if 'nametracesaccumulated' in traceNames:
            nametracesaccumulatedList = []
            for key in sorted(keyMap["name"].keys(), key=lambda x: x.lower()):
                thetrace = {'x': [], 'y': [], 'name': key + ' (accumulated)', 'type': 'scatter'}
                self._buildSumTrace(thetrace=thetrace, key=key, dateValueDict=keyMap["name"][key], legendonlyTraces=legendonlyTraces)
                nametracesaccumulatedList.append(thetrace)
            traces["nametracesaccumulated"] = nametracesaccumulatedList

        result = {'traces': traces}
        if 'scatter' in traceNames:
            scatter = {'timestamp': [], 'account': [], 'id': [], 'amount': [], 'category': [], 'currency': [], 'name': [], 'description': [], 'note': [], 'theX': []}
            # 'mode': 'markers', 'type': 'scatter', 'visible': 'legendonly', 'name': 'Einzelumsätze', 'text': [], 'marker': {'size': 5, 'opacity': 0.5}
            scatterlist = sorted(scatterlist, key=lambda x: x[sortScatterBy], reverse=sortScatterByReverse)
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

        return result


    def validateRules(self, transactions):
        categories = self.parseCategories()
        rules = []
        for c in categories:
            if c["expectedValue"] is not None:
                rules.append(c)

        validationOverview = []
        for rule in rules:
            sum = 0.0
            for transaction in transactions["transactions"]:
                if rule['compiledPattern'].search(transaction[rule['field']]):
                    sum += transaction["amount"]
            if sum < rule["expectedValue"]:
                validationOverview.append({"type": "warning", "category": rule["category"], "current": "{:.2f}".format(sum), "expectedint": rule["expectedValue"], "expected": "{:.2f}".format(rule["expectedValue"])})
            else:
                validationOverview.append({"type": "ok", "category": rule["category"], "current": "{:.2f}".format(sum), "expectedint": rule["expectedValue"], "expected": "{:.2f}".format(rule["expectedValue"])})
        validationOverview = sorted(validationOverview, key=lambda rr: rr["expectedint"], reverse=True)

        return validationOverview


    def hasEntry(self, tableName, entry):
        sqlparts = []
        sqlparams = []
        for k, v in entry.items():
            sqlparts.append(k + '=?')
            sqlparams.append(v)

        self.cursor.execute('SELECT * FROM ' + tableName + ' WHERE ' + (' AND '.join(sqlparts)), sqlparams)
        row = self.cursor.fetchone()
        if row is None:
            return False
        return True

    def hasTransactionEntry(self, entry):
        e = dict(entry)
        e["timestamp"] = calendar.timegm(datetime.datetime.strptime(e["date"], '%d.%m.%Y').utctimetuple())
        e.pop("date", None)
        return self.hasEntry(tableName="transactions", entry=e)

    def updateEntry(self, tableName, theid, entry):
        sqlparts = []
        sqlparams = []
        for k, v in entry.items():
            sqlparts.append(k + '=?')
            sqlparams.append(v)

        if len(sqlparams) == 0:
            return False
        sqlparams.append(theid)
        self.cursor.execute('UPDATE ' + tableName + ' SET ' + (','.join(sqlparts)) + ' WHERE rowid=?', sqlparams)
        self.conn.commit()
        return True

    def deleteItem(self, tableName, theid):
        self.cursor.execute('DELETE FROM ' + tableName + ' WHERE rowid=?', [theid])
        self.conn.commit()
