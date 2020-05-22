#!/usr/bin/env python3
# coding=utf-8


from bottle import Bottle, static_file, request, template, run, auth_basic
#from bottle import jinja2_view as view, jinja2_template as template
import datetime
import dateutil.relativedelta
import calendar
import json
import sys
import re
import os
import io
import csv
import codecs
import locale
import json
import hashlib

import kontomodel

configdata = None

class MyBottle(Bottle):
    def default_error_handler(self, error):
        return str(error).replace("\\n", "\n")

app = MyBottle()
#app = Bottle()

def getKonto():
    return kontomodel.KontoModel(sqlitefile='konto.sqlite')

def check_pass(username, password):
    global configdata
    return configdata is None or (('username' not in configdata or configdata['username'] is None or configdata['username'] == username) and ('passwordsha224' not in configdata or configdata['passwordsha224'] is None or configdata['passwordsha224'] == hashlib.sha224(password.encode()).hexdigest()))

@app.route('/static/<thefilename:path>')
@auth_basic(check_pass)
def server_static(thefilename):
    return static_file(thefilename, root='static')


@app.route('/')
@app.route('/byCategory/<byCategory>')
@auth_basic(check_pass)
def indexFile(byCategory='month'):
    k = getKonto()
    accounts = k.getAccounts()
    categoriesNames = k.getCategoriesNames()
    return template('index.tpl', title='Ausgaben', site=byCategory, byCategory=byCategory, tracesJSON=json.dumps(['traces', 'profit']), accounts=accounts, categoriesNames=categoriesNames)


@app.route('/sum')
@auth_basic(check_pass)
def profit():
    k = getKonto()
    accounts = k.getAccounts()
    categoriesNames = k.getCategoriesNames()
    return template('index.tpl', title='Aufsummiert seit %fromDate%', site='sum', byCategory='month', tracesJSON=json.dumps(['profit', 'totalprofit', 'tracessum']), accounts=accounts, categoriesNames=categoriesNames)


@app.route('/getConsolidated', method="POST")
@auth_basic(check_pass)
def getConsolidated():
    k = getKonto()
    byCategory = request.json.get('byCategory')
    traces = request.json.get('traces')

    fromDateJSON = request.json.get('fromDate', None)
    fromDate = None
    if fromDateJSON is not None:
        fromDate = datetime.datetime.strptime(fromDateJSON + " 00:00:00.000000", '%Y-%m-%d %H:%M:%S.%f')

    toDateJSON = request.json.get('toDate', None)
    toDate = None
    if toDateJSON is not None:
        toDate = datetime.datetime.strptime(toDateJSON + " 23:59:59.999999", '%Y-%m-%d %H:%M:%S.%f')

    accounts = request.json.get('accounts')
    patternInput = request.json.get('patternInput')
    thepattern = None if len(patternInput) == 0 else patternInput

    minAmount = request.json.get('minAmount', None)
    maxAmount = request.json.get('maxAmount', None)

    legendonlyTraces = ["Umbuchung", "Gehalt"]
    transactions = k.getTransactions(accounts=accounts, fromDate=fromDate, toDate=toDate, minAmount=minAmount, maxAmount=maxAmount, categorySelection=None, thepattern=thepattern)
    consolidated = k.getConsolidated(transactions=transactions["transactions"], byCategory=byCategory, traceNames=traces, sortScatterBy='timestamp', sortScatterByReverse=True, legendonlyTraces=legendonlyTraces)

    # return json.dumps(request.json.get('items'))
    return json.dumps({'traces': consolidated['traces'], 'foundDuplicates': transactions['foundDuplicates']})


@app.route('/transactions/getDetails', method="POST")
@auth_basic(check_pass)
def getDetails():
    k = getKonto()
    theX = request.json.get('theX')
    xfield = request.json.get('xfield', 'theX')
    byCategory = request.json.get('byCategory')

    fromDateJSON = request.json.get('fromDate', None)
    fromDate = None
    if fromDateJSON is not None:
        fromDate = datetime.datetime.strptime(fromDateJSON + " 00:00:00.000000", '%Y-%m-%d %H:%M:%S.%f')

    toDateJSON = request.json.get('toDate', None)
    toDate = None
    if toDateJSON is not None:
        toDate = datetime.datetime.strptime(toDateJSON + " 23:59:59.999999", '%Y-%m-%d %H:%M:%S.%f')

    accounts = request.json.get('accounts')
    patternInput = request.json.get('patternInput')
    thepattern = None if patternInput is None or len(patternInput) == 0 else patternInput
    categorySelection = request.json.get('categorySelection')

    sortScatterBy = request.json.get('sortScatterBy')
    sortScatterByReverse = request.json.get('sortScatterByReverse')

    csvexport = request.json.get('csvexport', False)

    title = 'Umsätze'
    if categorySelection is not None:
        if len(categorySelection) == 1:
            title = title + template(' der Kategorie "{{x}}"', x=categorySelection[0])
        elif len(categorySelection) > 1:
            title = title + template(' der Kategorien {{x}}', x=(", ".join(categorySelection)))

    if theX is not None:
        title = title + template(' für {{theX}}', theX=theX)
    minAmount = request.json.get('minAmount', None)
    maxAmount = request.json.get('maxAmount', None)

    legendonlyTraces = ["Umbuchung", "Gehalt"]
    transactions = k.getTransactions(accounts=accounts, fromDate=fromDate, toDate=toDate, minAmount=minAmount, maxAmount=maxAmount, categorySelection=categorySelection, thepattern=thepattern)
    consolidated = k.getConsolidated(transactions=transactions["transactions"], byCategory=byCategory, traceNames=['scatter'], sortScatterBy=sortScatterBy, sortScatterByReverse=sortScatterByReverse, legendonlyTraces=legendonlyTraces)

    thescatter = consolidated['scatter']
    if csvexport:
        cwriterresult = io.StringIO()
        cwriter = csv.DictWriter(cwriterresult, fieldnames=['id', 'date', 'x', 'account', 'amount', 'currency', 'name', 'description', 'category', 'note'], delimiter=',')
        cwriter.writeheader()
        for i in range(0, len(thescatter['timestamp'])):
            if theX is None or theX == thescatter['theX'][i]:
                mydate = datetime.datetime.fromtimestamp(thescatter['timestamp'][i]).strftime('%Y-%m-%d')
                cwriter.writerow({'date': mydate,
                                'account': thescatter['account'][i],
                                'id': thescatter['id'][i],
                                'amount': thescatter['amount'][i],
                                'currency': thescatter['currency'][i],
                                'name': thescatter['name'][i],
                                'description': thescatter['description'][i],
                                'category': thescatter['category'][i],
                                'note': thescatter['note'][i],
                                'x': thescatter['theX'][i]})
        cwriterresultstr = cwriterresult.getvalue()
        cwriterresult.close()
        return cwriterresultstr
    else:
        result = []
        for i in range(0, len(thescatter['timestamp'])):
            if theX is None or theX == thescatter['theX'][i]:
                mydate = datetime.datetime.fromtimestamp(thescatter['timestamp'][i]).strftime('%Y-%m-%d')
                result.append({ 'date': mydate,
                                'account': thescatter['account'][i],
                                'id': thescatter['id'][i],
                                'amountint': thescatter['amount'][i],
                                'amount': "{:.2f}".format(thescatter['amount'][i]),
                                'currency': thescatter['currency'][i],
                                'name': thescatter['name'][i],
                                'description': thescatter['description'][i],
                                'category': thescatter['category'][i],
                                'note': thescatter['note'][i],
                                'x': thescatter['theX'][i]})
        return json.dumps({"title": title, "data": result})


@app.route('/check/<yearmonth>/<lastMonths>/<includeHeader>')
@auth_basic(check_pass)
def check(yearmonth, lastMonths, includeHeader):
    result = {}
    k = getKonto()
    categories = k.parseCategories()
    categoryOverview = {}
    transactionsByNameOverview = {}
    profitOverview = {}
    rules = []
    for c in categories:
        if c["expectedValue"] is not None:
            rules.append(c)

    firstDayOfMonth = None
    if yearmonth == "current" or yearmonth == "previous":
        firstDayOfMonth = datetime.datetime.today()
    else:
        firstDayOfMonth = datetime.datetime.strptime(yearmonth, "%Y-%m")

    for i in range(0, int(lastMonths)):
        firstDayOfMonth = datetime.datetime(year=firstDayOfMonth.year, month=firstDayOfMonth.month, day=1, hour=0, minute=0, second=0, microsecond=0)

        if yearmonth != "previous" or i == 1:
            _, num_days = calendar.monthrange(firstDayOfMonth.year, firstDayOfMonth.month)
            lastDayOfMonth = datetime.datetime(year=firstDayOfMonth.year, month=firstDayOfMonth.month, day=num_days, hour=23, minute=59, second=59, microsecond=999999)
            monthString = firstDayOfMonth.strftime("%m/%Y")
            result[monthString] = []

            transactions = k.getTransactions(accounts=None, fromDate=firstDayOfMonth, toDate=lastDayOfMonth, minAmount=None, maxAmount=None, categorySelection=None, thepattern=None)
            consolidated = k.getConsolidated(transactions=transactions["transactions"], byCategory="month", traceNames=["traces", "profit"], sortScatterBy='timestamp', sortScatterByReverse=True, legendonlyTraces=["Umbuchung", "Gehalt"])

            transactionsByName = {}
            for t in transactions["transactions"]:
                if len(t["name"].strip()) == 0 and t["amount"] == 0:
                    continue
                if t["name"] not in transactionsByName:
                    transactionsByName[t["name"]] = 0
                transactionsByName[t["name"]] = transactionsByName[t["name"]] + t["amount"]
            transactionsList = []
            for tname, tvalue in sorted(transactionsByName.items(), key=lambda kk: kk[1]):
                transactionsList.append({"name": tname, "sum": "{:.2f}".format(tvalue)})
            transactionsByNameOverview[monthString] = transactionsList

            coList = []
            profit = None
            for trace in consolidated["traces"]:
                category = trace["name"]
                assert(len(trace["x"]) <= 1)
                for i in range(0, len(trace["x"])):
                    x = trace["x"][i]
                    y = trace["y"][i]
                    if category == "Gewinn":
                        assert(profit is None)
                        profit = "{:.2f}".format(y)
                    else:
                        coList.append({"category": category, "sumint": y, "sum": "{:.2f}".format(y)})
            categoryOverview[monthString] = sorted(coList, key=lambda co: co["sumint"])
            profitOverview[monthString] = profit

            for rule in rules:
                sum = 0
                for transaction in transactions["transactions"]:
                    if rule['compiledPattern'].search(transaction[rule['field']]):
                        sum += transaction["amount"]
                if sum < rule["expectedValue"]:
                    result[monthString].append({"type": "warning", "category": rule["category"], "current": "{:.2f}".format(sum), "expectedint": rule["expectedValue"], "expected": "{:.2f}".format(rule["expectedValue"])})
                else:
                    result[monthString].append({"type": "ok", "category": rule["category"], "current": "{:.2f}".format(sum), "expectedint": rule["expectedValue"], "expected": "{:.2f}".format(rule["expectedValue"])})
            result[monthString] = sorted(result[monthString], key=lambda rr: rr["expectedint"], reverse=True)

        firstDayOfMonth = firstDayOfMonth - dateutil.relativedelta.relativedelta(months=1)

    return template('check.tpl', site="check", months=result, includeHeader=includeHeader, profitOverview=profitOverview, categoryOverview=categoryOverview, transactionsByNameOverview=transactionsByNameOverview)


@app.route('/uploadCSV', method='GET')
@auth_basic(check_pass)
def uploadCSV():
    return template('uploadCSV.tpl', site='uploadCSV')


@app.route('/uploadCSV', method='POST')
@auth_basic(check_pass)
def uploadCSVPost():
    upload = request.files.get("upload")
    cfile = codecs.iterdecode(upload.file, request.forms.getunicode('encoding'))
    for i in range(0, int(request.forms.getunicode('skiplines'))):
        next(cfile)
    reader = csv.reader(cfile, delimiter=request.forms.getunicode('delimiter'))
    k = getKonto()

    account = request.forms.getunicode('account')
    dateformat = request.forms.getunicode('dateformat')
    thelocale = request.forms.getunicode('locale')
    daterow = int(request.forms.getunicode('daterow'))
    namerow = int(request.forms.getunicode('namerow'))
    descriptionrow = int(request.forms.getunicode('descriptionrow'))
    amountrow = int(request.forms.getunicode('amountrow'))

    currencyrowstr = request.forms.getunicode('currencyrow')
    currencyrow = None
    if currencyrowstr is not None and len(currencyrowstr.strip()) != 0:
        currencyrow = int(currencyrowstr)

    sollhabenrowstr = request.forms.getunicode('sollhabenrow')
    sollhabenrow = None
    if sollhabenrowstr is not None and len(sollhabenrowstr.strip()) != 0:
        sollhabenrow = int(sollhabenrowstr)

    locale.setlocale(locale.LC_ALL, thelocale)

    content = []
    i = 0
    for row in reader:
        if len(row) == 0:
            continue
        startOfDay = datetime.datetime.strptime(row[daterow] + " 00:00:00.000000", dateformat + " %H:%M:%S.%f")
        endOfDay = datetime.datetime.strptime(row[daterow] + " 23:59:59.999999", dateformat + " %H:%M:%S.%f")
        thedate = datetime.datetime.strptime(row[daterow], dateformat).strftime("%d.%m.%Y")
        name = row[namerow].replace("\n", "")
        description = row[descriptionrow].replace("\n", "")
        amount = locale.atof(row[amountrow])
        currency = "" if currencyrow is None else row[currencyrow]
        sollhaben = None if sollhabenrow is None else row[sollhabenrow]
        if sollhaben == "S":
            amount = amount * -1.0
        errorstr = None

        if currency != '€' and currency != "EUR" and currency != "":
            errorstr = "currency is not EURO: " + currency
        else:
            dupe = {"date": datetime.datetime.strptime(row[daterow], dateformat).strftime("%d.%m.%Y"),
                    "account": account,
                    "name": name,
                    "amount": amount}
            if k.hasTransactionEntry(entry=dupe):
                errorstr = "possible duplicate found"

        ne = {"date": thedate, "name": name, "description": description, "amountint": amount, "amount": "{:.2f}".format(amount), "error": errorstr}
        content.append(ne)

    #upload.save("/tmp/test.txt")
    return template('uploadTransactions.tpl', site='uploadCSV', account=account, content=content)


@app.route('/uploadTransactions', method='POST')
@auth_basic(check_pass)
def uploadTransactionsPost():
    entries = request.json.get('entries')
    account = request.json.get('account')

    k = getKonto()
    ids = []
    for e in entries:
        theid = k.createTransactionEntry(entry={
              "date": e["date"],
              "name": e["name"],
              "description": e["description"],
              "amount": e["amount"],
              "account": account,
              "currency": "",
              "category": None,
              "note": None
            })
        ids.append(theid)
    return str(len(ids)) + " entries imported."


@app.route('/transactions/createEntry', method='POST')
@auth_basic(check_pass)
def createEntry():
    k = getKonto()

    entry = request.json.get('entry')
    if entry["amount"] is None or entry["amount"] == "":
        entry["amount"] = 0
    else:
        entry["amount"] = float(entry["amount"])
    if entry["date"] is not None:
        entry['date'] = datetime.datetime.strptime(entry['date'], "%Y-%m-%d").strftime("%d.%m.%Y")
    if "currency" not in entry:
        entry["currency"] = ""
 
    theid = k.createTransactionEntry(entry=entry)
    return json.dumps({'eid': theid})


@app.route('/categories/createEntry', method='POST')
@auth_basic(check_pass)
def createCategoryEntry():
    k = getKonto()
    entry = request.json.get('entry')
    theid = k.createCategoryEntry(entry=entry)
    return json.dumps({'eid': theid})


@app.route('/editCategories', method='GET')
@auth_basic(check_pass)
def editCategories(thefilename='categories'):
    k = getKonto()

    toDate = datetime.datetime.today()
    fromDate = toDate - dateutil.relativedelta.relativedelta(months=6)
    toDateStr = toDate.strftime('%Y-%m-%d');
    fromDateStr = fromDate.strftime('%Y-%m-%d');

    categories = k.parseCategories()
    categoriesNames = k.getCategoriesNames()
    return template('editCategories.tpl', categories=categories, fromDate=fromDateStr, toDate=toDateStr, categoriesNames=categoriesNames)


@app.route('/categories/updateEntry/<theid>', method='POST')
@auth_basic(check_pass)
def categoriesUpdateEntry(theid):
    k = getKonto()
    entry = {}
    theentry = request.json.get('entry')
    if "category" in theentry:
        entry["category"] = theentry["category"]
    if "field" in theentry:
        entry["field"] = theentry["field"]
    if "pattern" in theentry:
        entry["pattern"] = theentry["pattern"]
    if "expectedValue" in theentry:
        entry["expectedValue"] = theentry["expectedValue"]
    if "priority" in theentry:
        entry["priority"] = theentry["priority"]
    k.updateEntry(tableName="categories", theid=theid, entry=entry)


@app.route('/transactions/updateEntry/<theid>', method="POST")
@auth_basic(check_pass)
def transactionsUpdateEntry(theid):
    k = getKonto()
    entry = {}
    theentry = request.json.get('entry')
    if "date" in theentry:
        thedate = theentry["date"]
        entry["timestamp"] = calendar.timegm(datetime.datetime.strptime(thedate, '%Y-%m-%d').utctimetuple())
    if "account" in theentry:
        entry["account"] = theentry["account"]
    if "name" in theentry:
        entry["name"] = theentry["name"]
    if "description" in theentry:
        entry["description"] = theentry["description"]
    if "category" in theentry:
        entry["category"] = theentry["category"]
    if "note" in theentry:
        entry["note"] = theentry["note"]
    k.updateEntry(tableName="transactions", theid=theid, entry=entry)


@app.route('/categories/deleteEntry/<theid>', method="GET")
@auth_basic(check_pass)
def categoriesDeleteEntry(theid):
    k = getKonto()
    k.deleteItem(tableName="categories", theid=theid)


@app.route('/transactions/deleteEntry/<theid>', method="GET")
@auth_basic(check_pass)
def transactionsDeleteEntry(theid):
    k = getKonto()
    k.deleteItem(tableName="transactions", theid=theid)


if __name__ == "__main__":
    if os.path.isfile('/etc/konto.config'):
        with open('/etc/konto.config', 'r') as thefile:
            configdata = json.load(thefile)

    if len(sys.argv) > 1 and sys.argv[1] == 'dev':
        print('using dev engine')
        run(app, host='0.0.0.0', port=8080)
    else:
        print('using bjoern engine')
        run(app, server='bjoern', host='0.0.0.0', port=8080)

