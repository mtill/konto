#!/usr/bin/env python3
# coding=utf-8

import os
import time
import re
import html


def doLock(thefilename, thepath='lists/'):
    while os.path.exists(thepath + thefilename + '.lock'):
        time.sleep(1)
    with open(thepath + thefilename + '.lock', 'w') as thelockfile:
        thelockfile.write('lock')

def doUnlock(thefilename, thepath='lists/'):
    os.remove(thepath + thefilename + '.lock')

def findCategory(theitem, categories, unknownCategory='nicht kategorisiert'):
    for category in categories:
        if re.search(category['pattern'], theitem[category['field']]):
            return category['category']
    return unknownCategory

def writeCategories(categoriesString, thepath='lists/', thefilename='categories'):
    doLock(thefilename=thefilename, thepath=thepath)
    with open(thepath + thefilename + '.txt', 'w') as f:
        f.write(categoriesString)
    doUnlock(thefilename=thefilename, thepath=thepath)

def parseCategories(thefilename='categories', thepath='lists/'):
    result = []
    with open(thepath + thefilename + '.txt', 'r') as f:
        for line in f:
            line = line.strip()
            if len(line) == 0 or line[0] == '#':
                continue
            categoryEnd = line.find(';')
            fieldEnd = line.find(';', categoryEnd+1)
            result.append({'pattern': line[fieldEnd+1:],
                           'field': line[categoryEnd+1:fieldEnd],
                           'category': line[0:categoryEnd]})
    return result

def readCategoriesFile(thefilename='categories', thepath='lists/'):
    categories = ''
    with open(thepath + thefilename + '.txt', 'r') as f:
        categories = f.read()
    return categories

def parseFiles(thefilenames):
    result = []
    for thefilename in thefilenames:
        result.extend(parseFile(thefilename))
    return result

def parseListLine(line):
    tmp = line.strip()
    if len(tmp) == 0 or tmp[0] == '#':
        return None

    linesplit = line.split(';')
    # if len(linesplit) != 6:
    #     raise Exception('invalid data format')
    currency = linesplit[2].strip()
    if currency != '€':
        raise Exception('unknown currency ' + currency)
    thecategory = ';'.join(linesplit[5:]).strip()

    return {'date': linesplit[0].strip().replace('/', '-'),
            'amount': float(linesplit[1].strip()),
            'currency': currency,
            'name': linesplit[3].strip(),
            'title': linesplit[4].strip(),
            'category': thecategory}

def parseFile(thefilename, thepath='lists/'):
    result = []
    linepos = 0
    with open(thepath + thefilename + '.list', 'r') as f:
        for line in f:
            parsedLine = parseListLine(line)
            if parsedLine is not None:
                # thehash = str(hashlib.md5((parsedLine['date'] + str(parsedLine['amount']) + parsedLine['currency'] + parsedLine['name'] + parsedLine['title']).encode()).hexdigest())
                parsedLine['id'] = thefilename + '_' + str(linepos)
                linepos = linepos + 1
                result.append(parsedLine)
    return result

def writeFile(thefilename, filecontent, thepath='lists/'):
    with open(thepath + thefilename + '.list', 'w') as thefile:
        for line in filecontent:
            thefile.write(line['date'] + ';' + str(line['amount']) + ';' + line['currency'] + ';' + line['name'] + ';' + line['title'] + ';' + line['category'] + '\n')

def getLists(thepath='lists'):
    result = []
    for (dirpath, dirnames, filenames) in os.walk(thepath):
        for filename in filenames:
            if filename.endswith('.list'):
                result.append(filename[0:-5])
        break
    return sorted(result)

def getConsolidated(byCategory, traceNames, fromDate, toDate, categories, thepath='lists/'):
    filecontent = parseFiles(getLists(thepath=thepath))
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

    for f in filecontent:
        if len(f['category']) == 0:
            dupLine = f['date'] + ' ' + str(f['amount']) + ' ' + f['currency'] + ' ' + f['name'] + ' ' + f['title']
            if dupLine in duplicatesMap:
                foundDuplicates.append(html.escape(dupLine))
            else:
                duplicatesMap[dupLine] = True
            f['category'] = findCategory(theitem=f, categories=categories)
        else:
            if f['category'] not in allcategoriesNames:
                allcategoriesNames.append(f['category'])

        thedate = time.strptime(f['date'], '%Y-%m-%d')
        theX = f['date']
        if (fromDate is None or thedate >= fromDate) and (toDate is None or thedate <= toDate):
            if byCategory == 'month' or byCategory == 'profit':
                theX = f['date'][0:7]
            elif byCategory == 'year':
                theX = f['date'][0:4]
            elif byCategory == 'day':
                theX = f['date']

            f['theX'] = theX
            scatterlist.append(f)

            if theX not in sumdict:
                sumdict[theX] = 0
            sumdict[theX] += f['amount']

            if f['category'] not in allcategories:
                allcategories[f['category']] = {}
            xy = f['amount']
            if xy <= 0:
                xy = abs(xy)
                if theX in allcategories[f['category']]:
                    xy = xy + allcategories[f['category']][theX]
                allcategories[f['category']][theX] = xy
            else:
                if theX not in incomedict:
                    incomedict[theX] = 0
                incomedict[theX] += f['amount']

    traces = []
    if 'profit' in traceNames:
        profit = {'x': [], 'y': [], 'name': 'Gewinn', 'type': 'scatter'}
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
            for tracekey in sorted(allcategories[key].keys()):
                thetrace['x'].append(tracekey)
                thetrace['y'].append(allcategories[key][tracekey])
            traces.append(thetrace)

    result = {'traces': traces, 'foundDuplicates': foundDuplicates}
    if 'scatter' in traceNames:
        scatter = {'date': [], 'id': [], 'amount': [], 'category': [], 'currency': [], 'name': [], 'title': [], 'theX': []}
        # 'mode': 'markers', 'type': 'scatter', 'visible': 'legendonly', 'name': 'Einzelumsätze', 'text': [], 'marker': {'size': 5, 'opacity': 0.5}
        scatterlist = sorted(scatterlist, key=lambda x: x['date'])
        for x in scatterlist:
            scatter['date'].append(x['date'])
            scatter['id'].append(x['id'])
            scatter['amount'].append(x['amount'])
            scatter['currency'].append(x['currency'])
            scatter['category'].append(x['category'])
            # scatter['text'].append(x['name'] + ' ' + x['title'])
            scatter['name'].append(x['name'])
            scatter['title'].append(x['title'])
            scatter['theX'].append(x['theX'])
        result['scatter'] = scatter

    result['allcategoriesNames'] = sorted(allcategoriesNames, key=lambda x: x.lower())
    return result

def updateCategory(itemId, thecategory, thepath='lists/'):
    thefilenames = getLists(thepath)
    for thefilename in thefilenames:
        content = parseFile(thefilename, thepath=thepath)
        for c in content:
            if c['id'] == itemId:
                c['category'] = thecategory

                doLock(thefilename=thefilename, thepath=thepath)
                writeFile(thefilename=thefilename, filecontent=content, thepath=thepath)
                doUnlock(thefilename=thefilename, thepath=thepath)
                return True
    return False

def convertToItem(scatter, pos):
    return {
        'date': scatter['date'][i],
        'amount': scatter['amount'][i],
        'currency': scatter['currency'][i],
        'name': scatter['name'][i],
        'title': scatter['title'][i],
        'category': scatter['category'][i],
        'id': scatter['id'][i]
    }

def getUncategorizedItems():
    categories = parseCategories()
    consolidated = getConsolidated(byCategory='month', traceNames=['scatter'], fromDate=None, categories=categories, toDate=None)
    scatter = consolidated['scatter']

    result = {}
    result['allcategoriesNames'] = consolidated['allcategoriesNames']
    resultItems = {'date': [], 'id': [], 'amount': [], 'category': [], 'currency': [], 'name': [], 'title': [], 'theX': []}
    for i in range(0, len(scatter['date'])):
        if scatter['category'][i] == '' or scatter['category'][i] == 'nicht kategorisiert':
            resultItems['date'].append(scatter['date'][i])
            resultItems['id'].append(scatter['id'][i])
            resultItems['amount'].append(scatter['amount'][i])
            resultItems['currency'].append(scatter['currency'][i])
            resultItems['category'].append(scatter['category'][i])
            resultItems['name'].append(scatter['name'][i])
            resultItems['title'].append(scatter['title'][i])
            resultItems['theX'].append(scatter['theX'][i])
    result['items'] = resultItems
    return result
