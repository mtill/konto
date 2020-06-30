#!/usr/bin/env python3
# coding=utf-8


from bottle import Bottle, static_file, request, template, run, auth_basic
#from bottle import jinja2_view as view, jinja2_template as template
import datetime
import dateutil.relativedelta
import calendar
import json
import csv
import sys
import re
import os
import io
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
@auth_basic(check_pass)
def indexFile():
    k = getKonto()
    accounts = k.getAccounts()
    categoriesNames = k.getCategoriesNames()
    return template('index.tpl', title="debits and credits", site='index', accounts=accounts, categoriesNames=categoriesNames)


def buildTitle(categorySelection, fromDate, toDate):
    title = ''
    if categorySelection is not None:
        if len(categorySelection) == 1:
            title = title + template(', category "{{x}}"', x=categorySelection[0])
        elif len(categorySelection) > 1:
            title = title + template(', categories {{x}}', x=(", ".join(categorySelection)))
    title = title + ' (' + fromDate.strftime("%Y-%m-%d") + " - " + toDate.strftime("%Y-%m-%d") + ")"
    return title


@app.route('/getConsolidated', method="POST")
@auth_basic(check_pass)
def getConsolidated():
    k = getKonto()
    groupBy = request.json.get('groupBy')
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

    legendonlyTraces = ["transfer", "income"]
    transactions = k.getTransactions(accounts=accounts, fromDate=fromDate, toDate=toDate, minAmount=minAmount, maxAmount=maxAmount, categorySelection=None, thepattern=thepattern)
    consolidated = k.getConsolidated(transactions=transactions["transactions"], groupBy=groupBy, traceNames=traces, sortScatterBy='timestamp', sortScatterByReverse=True, legendonlyTraces=legendonlyTraces)

    thetraces = []
    for t in consolidated['traces'].values():
        thetraces.extend(t)

    # return json.dumps(request.json.get('items'))
    return json.dumps({'traces': thetraces,
                       'title': buildTitle(categorySelection=None, fromDate=fromDate, toDate=toDate),
                       'foundDuplicates': transactions['foundDuplicates']
                       })


def _prepareTraces(traces, nametraces):
    transactionsByName = nametraces
    transactionsByNameOverview = []
    for transactionByName in transactionsByName:
        y = 0.0
        values = transactionByName["y"]
        for i in range(0, len(values)):
            y += values[i]
        transactionsByNameOverview.append({"name": transactionByName["name"], "sumint": y, "sum": "{:.2f}".format(y)})
    transactionsByNameOverview = sorted(transactionsByNameOverview, key=lambda x: x["sumint"])

    categoryOverview = []
    for trace in traces:
        category = trace["name"]
        y = 0.0
        for i in range(0, len(trace["y"])):
            y += trace["y"][i]
        categoryOverview.append({"category": category, "sumint": y, "sum": "{:.2f}".format(y)})
    categoryOverview = sorted(categoryOverview, key=lambda co: co["sumint"])
    return {"transactionsByName": transactionsByNameOverview, "transactionsByCategory": categoryOverview}


@app.route('/transactions/getDetails', method="POST")
@auth_basic(check_pass)
def getDetails():
    k = getKonto()
    groupBy = request.json.get('groupBy')

    fromDateJSON = request.json.get('fromDate', None)
    fromDate = None
    if fromDateJSON is not None:
        fromDate = datetime.datetime.strptime(fromDateJSON + " 00:00:00.000000", '%Y-%m-%d %H:%M:%S.%f')

    toDateJSON = request.json.get('toDate', None)
    toDate = None
    if toDateJSON is not None:
        toDate = datetime.datetime.strptime(toDateJSON + " 23:59:59.999999", '%Y-%m-%d %H:%M:%S.%f')

    theX = request.json.get('theX')
    if theX is not None:
        if groupBy == 'week':
            xfrom = datetime.datetime.strptime(theX + " 1 00:00:00.000000", '%G-week %V %w %H:%M:%S.%f')
            xto = xfrom + datetime.timedelta(days=6)
            xto = datetime.datetime(year=xto.year, month=xto.month, day=xto.day, hour=23, minute=59, second=59, microsecond=999999)

        elif groupBy == 'month':
            xfrom = datetime.datetime.strptime(theX + "-01 00:00:00.000000", '%Y-%m-%d %H:%M:%S.%f')
            _, num_days = calendar.monthrange(xfrom.year, xfrom.month)
            xto = datetime.datetime(year=xfrom.year, month=xfrom.month, day=num_days, hour=23, minute=59, second=59, microsecond=999999)

        elif groupBy == 'quarter':
            quarterPattern = re.compile('(\d\d\d\d)-quarter (\d+)')
            quarterMatch = quarterPattern.match(theX)
            theyearint = int(quarterMatch.group(1))
            thequarter = quarterMatch.group(2)
            themonthint = ((int(thequarter) - 1) * 3) + 1
            thelastmonthint = themonthint + 2

            xfrom = datetime.datetime(year=theyearint, month=themonthint, day=1, hour=0, minute=0, second=0, microsecond=0)
            _, num_days = calendar.monthrange(theyearint, thelastmonthint)
            xto = datetime.datetime(year=theyearint, month=thelastmonthint, day=num_days, hour=23, minute=59, second=59, microsecond=999999)

        elif groupBy == 'year':
            xfrom = datetime.datetime.strptime(theX + "-01-01 00:00:00.000000", '%Y-%m-%d %H:%M:%S.%f')
            _, num_days = calendar.monthrange(xfrom.year, 12)
            xto = datetime.datetime(year=xfrom.year, month=12, day=num_days, hour=23, minute=59, second=59, microsecond=999999)

        if xfrom > fromDate:
            fromDate = xfrom
        if xto < toDate:
            toDate = xto

    accounts = request.json.get('accounts')
    patternInput = request.json.get('patternInput')
    thepattern = None if patternInput is None or len(patternInput) == 0 else patternInput
    categorySelection = request.json.get('categorySelection')

    sortScatterBy = request.json.get('sortScatterBy')
    sortScatterByReverse = request.json.get('sortScatterByReverse')

    title = buildTitle(categorySelection=categorySelection, fromDate=fromDate, toDate=toDate)

    minAmount = request.json.get('minAmount', None)
    maxAmount = request.json.get('maxAmount', None)

    legendonlyTraces = ["transfer", "income"]
    transactions = k.getTransactions(accounts=accounts, fromDate=fromDate, toDate=toDate, minAmount=minAmount, maxAmount=maxAmount, categorySelection=categorySelection, thepattern=thepattern)
    consolidated = k.getConsolidated(transactions=transactions["transactions"], groupBy=groupBy, traceNames=['scatter', 'traces', 'nametraces'], sortScatterBy=sortScatterBy, sortScatterByReverse=sortScatterByReverse, legendonlyTraces=legendonlyTraces)

    thescatter = consolidated['scatter']
    validatedRules = k.validateRules(transactions=transactions)
    preparedTraces = _prepareTraces(traces=consolidated["traces"]["traces"], nametraces=consolidated["traces"]["nametraces"])

    result = []
    for i in range(0, len(thescatter['timestamp'])):
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
    return json.dumps({"title": title, "data": result, "validatedRules": validatedRules, "transactionsByName": preparedTraces["transactionsByName"], "transactionsByCategory": preparedTraces["transactionsByCategory"]})


@app.route('/check/<yearmonth>/<lastMonths>/<includeHeader>')
@auth_basic(check_pass)
def check(yearmonth, lastMonths, includeHeader):
    k = getKonto()
    categories = k.parseCategories()
    rules = []
    for c in categories:
        if c["expectedValue"] is not None:
            rules.append(c)

    firstDayOfMonth = None
    if yearmonth == "current" or yearmonth == "previous":
        firstDayOfMonth = datetime.datetime.today()
    else:
        firstDayOfMonth = datetime.datetime.strptime(yearmonth, "%Y-%m")

    aggregatedDetails = {}
    for i in range(0, int(lastMonths)):
        firstDayOfMonth = datetime.datetime(year=firstDayOfMonth.year, month=firstDayOfMonth.month, day=1, hour=0, minute=0, second=0, microsecond=0)

        if yearmonth != "previous" or i == 1:
            _, num_days = calendar.monthrange(firstDayOfMonth.year, firstDayOfMonth.month)
            lastDayOfMonth = datetime.datetime(year=firstDayOfMonth.year, month=firstDayOfMonth.month, day=num_days, hour=23, minute=59, second=59, microsecond=999999)
            monthString = firstDayOfMonth.strftime("%m/%Y")

            transactions = k.getTransactions(accounts=None, fromDate=firstDayOfMonth, toDate=lastDayOfMonth, minAmount=None, maxAmount=None, categorySelection=None, thepattern=None)
            consolidated = k.getConsolidated(transactions=transactions["transactions"], groupBy="month", traceNames=["traces", "nametraces", "profit"], sortScatterBy='timestamp', sortScatterByReverse=True, legendonlyTraces=["transfer", "income"])
            aggregatedDetails[monthString] = {}
            aggregatedDetails[monthString]["validatedRules"] = k.validateRules(transactions=transactions)
            preparedTraces = _prepareTraces(traces=consolidated["traces"]["traces"], nametraces=consolidated["traces"]["nametraces"])
            aggregatedDetails[monthString]["transactionsByName"] = preparedTraces["transactionsByName"]
            aggregatedDetails[monthString]["transactionsByCategory"] = preparedTraces["transactionsByCategory"]

        firstDayOfMonth = firstDayOfMonth - dateutil.relativedelta.relativedelta(months=1)

    return template('check.tpl', site="check", aggregatedDetails=aggregatedDetails, includeHeader=includeHeader)


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

