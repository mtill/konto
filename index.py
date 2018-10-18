#!/usr/bin/env python3
# coding=utf-8

from bottle import Bottle, static_file, request, template, run, auth_basic
import datetime
import json
import sys
import re
import os
import io
import csv
import json
import hashlib

import kontomodel

configdata = None
app = Bottle()

def getKonto():
    return kontomodel.KontoModel(sqlitefile='konto.sqlite')

def check_pass(username, password):
    global configdata
    return configdata is None or (('username' not in configdata or configdata['username'] is None or configdata['username'] == username) and ('passwordsha224' not in configdata or configdata['passwordsha224'] is None or configdata['passwordsha224'] == hashlib.sha224(password.encode()).hexdigest()))

@app.route('/')
@app.route('/byCategory/<byCategory>')
@auth_basic(check_pass)
def indexFile(byCategory='month'):
    accounts = getKonto().getAccounts()
    return template('index.tpl', title='Ausgaben', site=byCategory, byCategory=byCategory, tracesJSON=json.dumps(['traces', 'profit']), accounts=accounts)

@app.route('/addNewItem', method='POST')
@auth_basic(check_pass)
def addNewItem():
    thedate = request.json.get('newItemDate')
    theamount = request.json.get('newItemAmount')
    thename = request.json.get('newItemName')
    thedescription = request.json.get('newItemDescription')
    thecategory = request.json.get('newItemCategory')
    thenote = request.json.get('newItemNote')

    if thedate is None or thedate == '':
        raise Exception("invalid date")
    if theamount is None or theamount == '':
        raise Exception("invalid amount")
    if thename is None or thename == '':
        raise Exception("invalid name")
    if thedescription is None or thedescription == '':
        raise Exception("invalid description")

    theamount = float(theamount)
    theaccount = 'Bargeld'

    newItem = getKonto().addItem(thedate=thedate,
               theaccount=theaccount,
               theamount=theamount,
               thecurrency='€',
               thename=thename,
               thedescription=thedescription,
               thecategory=thecategory,
               thenote=thenote)

    amountcurrency = '{:.2f}'.format(newItem['amount']) + newItem['currency']
    thecategory = '' if newItem['category'] == 'nicht kategorisiert' else newItem['category']
    htmlentry = template('categoryItem.tpl',
                         date=thedate,
                         name=newItem['name'],
                         shortname=newItem['name'][0:20],
                         description=newItem['description'],
                         account=newItem['account'],
                         shortdescription=newItem['description'][0:40],
                         theid=newItem['id'],
                         amountcurrency=amountcurrency,
                         thecategory=thecategory,
                         thenote=newItem['note'])

    return json.dumps({'htmlentry': htmlentry, 'errormsg': ''})

@app.route('/profit')
@auth_basic(check_pass)
def profit():
    k = getKonto()
    accounts = k.getAccounts()
    return template('index.tpl', title='Gewinn', site='profit', byCategory='month', tracesJSON=json.dumps(['profit', 'totalprofit']), accounts=accounts)

@app.route('/static/<thefilename:path>')
@auth_basic(check_pass)
def server_static(thefilename):
    return static_file(thefilename, root='static')

@app.route('/editCategories', method='GET')
@auth_basic(check_pass)
def editCategories(thefilename='categories'):
    k = getKonto()
    categoriesRaw = k.getCategoriesAsString()
    uncategorized = k.getUncategorizedItems()
    return template('editCategories.tpl', categoriesRaw=categoriesRaw, allcategoriesNames=uncategorized['allcategoriesNames'], uncategorized=uncategorized['items'])

@app.route('/editCategories', method='POST')
@auth_basic(check_pass)
def submitCategories():
    try:
        getKonto().writeCategories(categoriesString=request.forms.getunicode('categories'))
    except ValueError as e:
        return str(e)

    return editCategories()

@app.route('/getConsolidated', method="POST")
@auth_basic(check_pass)
def getConsolidated():
    k = getKonto()
    categories = k.parseCategories()
    byCategory = request.json.get('byCategory')
    traces = request.json.get('traces')

    fromDateJSON = request.json.get('fromDate', None)
    fromDate = None
    if fromDateJSON is not None:
        fromDate = datetime.datetime.strptime(fromDateJSON, '%Y-%m-%d')

    toDateJSON = request.json.get('toDate', None)
    toDate = None
    if toDateJSON is not None:
        toDate = datetime.datetime.strptime(toDateJSON, '%Y-%m-%d')

    accounts = request.json.get('accounts')
    patternInput = request.json.get('patternInput')
    thepattern = None if len(patternInput) == 0 else patternInput

    minAmount = request.json.get('minAmount', None)
    maxAmount = request.json.get('maxAmount', None)

    legendonlyTraces = ["Umbuchung", "Gehalt"]
    consolidated = k.getConsolidated(byCategory=byCategory, traceNames=traces, fromDate=fromDate, categories=categories, toDate=toDate, accounts=accounts, thepattern=thepattern, legendonlyTraces=legendonlyTraces, minAmount=minAmount, maxAmount=maxAmount)

    # return json.dumps(request.json.get('items'))
    return json.dumps({'traces': consolidated['traces'], 'foundDuplicates': consolidated['foundDuplicates']})

@app.route('/updateItem', method="POST")
@auth_basic(check_pass)
def updateItem():
    itemId = request.json.get('itemId')
    thename = request.json.get('thename')
    thedescription = request.json.get('thedescription')
    theamount = request.json.get('theamount')
    thecategory = request.json.get('thecategory')
    thenote = request.json.get('thenote')
    getKonto().updateItem(itemId=itemId, thename=thename, thedescription=thedescription, theamount=theamount, thecategory=thecategory, thenote=thenote)

@app.route('/deleteItem', method="POST")
@auth_basic(check_pass)
def deleteItem():
    itemId = request.json.get('itemId')
    getKonto().deleteItem(itemId=itemId)

@app.route('/getDetails', method="POST")
@auth_basic(check_pass)
def getDetails():
    k = getKonto()
    theX = request.json.get('theX')
    categories = k.parseCategories()
    byCategory = request.json.get('byCategory')

    fromDateJSON = request.json.get('fromDate', None)
    fromDate = None
    if fromDateJSON is not None:
        fromDate = datetime.datetime.strptime(fromDateJSON, '%Y-%m-%d')

    toDateJSON = request.json.get('toDate', None)
    toDate = None
    if toDateJSON is not None:
        toDate = datetime.datetime.strptime(toDateJSON, '%Y-%m-%d')

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
    consolidated = k.getConsolidated(byCategory=byCategory, traceNames=['scatter'], fromDate=fromDate, categories=categories, toDate=toDate, accounts=accounts, thepattern=thepattern, categorySelection=categorySelection, sortScatterBy=sortScatterBy, legendonlyTraces=legendonlyTraces, minAmount=minAmount, maxAmount=maxAmount)

    if csvexport:
        cwriterresult = io.StringIO()
        cwriter = csv.DictWriter(cwriterresult, fieldnames=['id', 'date', 'x', 'account', 'amount', 'currency', 'name', 'description', 'category', 'note'], delimiter=',')
        cwriter.writeheader()
        thescatter = consolidated['scatter']
        for i in range(0, len(thescatter['timestamp'])):
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
        return template('categorize.tpl', title=title, theX=theX, allcategoriesNames=consolidated['allcategoriesNames'], scatter=consolidated['scatter'], reverseSort=sortScatterByReverse)


if __name__ == "__main__":
    if os.path.isfile('/etc/konto.config'):
        with open('/etc/konto.config', 'r') as thefile:
            configdata = json.load(thefile)

    if len(sys.argv) > 1 and sys.argv[1] == 'dev':
        print('using dev engine')
        run(app, host='0.0.0.0', port=8080)
    else:
        print('using cherrypy engine')
        run(app, server='cherrypy', host='0.0.0.0', port=8080)

