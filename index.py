#!/usr/bin/env python3
# coding=utf-8

from bottle import Bottle, static_file, request, template, run
import datetime
import json
import sys
import re

import kontomodel as konto

app = Bottle()

@app.route('/')
@app.route('/byCategory/<byCategory>')
def indexFile(byCategory='month'):
    lists = konto.getLists()
    accounts = konto.getAccounts()
    return template('index.tpl', title='Ausgaben', site=byCategory, options=lists, byCategory=byCategory, tracesJSON=json.dumps(['traces', 'profit']), accounts=accounts)

@app.route('/addNewItem', method='POST')
def addNewItem():
    thedate = request.json.get('newItemDate')
    theamount = request.json.get('newItemAmount')
    thename = request.json.get('newItemName')
    thetitle = request.json.get('newItemTitle')
    thedescription = request.json.get('newItemDescription')
    thecategory = request.json.get('newItemCategory')

    if thedate is None or thedate == '':
        raise Exception("invalid date")
    if theamount is None or theamount == '':
        raise Exception("invalid amount")
    if thename is None or thename == '':
        raise Exception("invalid name")
    if thetitle is None or thetitle == '':
        raise Exception("invalid title")
    thedateobj = datetime.datetime.strptime(thedate, '%Y-%m-%d')

    theamount = float(theamount)
    thefilename = 'Bargeld-' + datetime.datetime.now().strftime('%Y-%m')
    theaccount = 'Bargeld'

    newItem = konto.appendItem(thefilename=thefilename,
               thedate=thedate,
               theaccount=theaccount,
               theamount=theamount,
               thecurrency='€',
               thename=thename,
               thetitle=thetitle,
               thedescription=thedescription,
               thecategory=thecategory)

    amountcurrency = str(newItem['amount']) + newItem['currency']
    thecategory = '' if newItem['category'] == 'nicht kategorisiert' else newItem['category']
    htmlentry = template('categoryItem.tpl',
                         date=newItem['date'],
                         name=newItem['name'],
                         shortname=newItem['name'][0:20],
                         title=newItem['title'],
                         account=newItem['account'],
                         theid=newItem['id'],
                         shorttitle=newItem['title'][0:40],
                         amountcurrency=amountcurrency,
                         thecategory=thecategory,
                         description=newItem['description'])

    return json.dumps({'htmlentry': htmlentry, 'errormsg': ''})

@app.route('/profit')
def profit():
    lists = konto.getLists()
    accounts = konto.getAccounts()
    return template('index.tpl', title='Gewinn', site='profit', options=lists, byCategory='month', tracesJSON=json.dumps(['profit', 'totalprofit']), accounts=accounts)

@app.route('/static/<thefilename:path>')
def server_static(thefilename):
    return static_file(thefilename, root='static')

@app.route('/editCategories', method='GET')
def editCategories(thefilename='categories'):
    categoriesRaw = konto.readCategoriesFile()
    uncategorized = konto.getUncategorizedItems()
    return template('editCategories.tpl', categoriesRaw=categoriesRaw, allcategoriesNames=uncategorized['allcategoriesNames'], uncategorized=uncategorized['items'])

@app.route('/editCategories', method='POST')
def submitCategories():
    try:
        konto.writeCategories(categoriesString=request.forms.getunicode('categories'))
    except re.error as e:
        return 'invalid regex: ' + str(e)

    return editCategories()

@app.route('/getConsolidated', method="POST")
def getConsolidated():
    categories = konto.parseCategories()
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

    consolidated = konto.getConsolidated(byCategory=byCategory, traceNames=traces, fromDate=fromDate, categories=categories, toDate=toDate, accounts=accounts, thepattern=thepattern)

    # return json.dumps(request.json.get('items'))
    return json.dumps({'traces': consolidated['traces'], 'foundDuplicates': consolidated['foundDuplicates']})

@app.route('/updateItem', method="POST")
def updateItem():
    itemId = request.json.get('itemId')
    thename = request.json.get('thename')
    thetitle = request.json.get('thetitle')
    theamount = request.json.get('theamount')
    thecategory = request.json.get('thecategory')
    thedescription = request.json.get('thedescription')
    konto.updateItem(itemId=itemId, thename=thename, thetitle=thetitle, theamount=theamount, thecategory=thecategory, thedescription=thedescription)

@app.route('/getDetails', method="POST")
def getDetails():
    theX = request.json.get('theX')
    categories = konto.parseCategories()
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

    theaction = request.json.get('action')
    theactionParam = request.json.get('actionParam')

    if theaction == 'deleteItem':
        konto.deleteEntry(theactionParam)

    title = 'Umsätze'
    if categorySelection is not None:
        if len(categorySelection) == 1:
            title = title + template(' der Kategorie "{{x}}"', x=categorySelection[0])
        elif len(categorySelection) > 1:
            title = title + template(' der Kategorien {{x}}', x=(", ".join(categorySelection)))

    if theX is not None:
        title = title + template(' für {{theX}}', theX=theX)

    consolidated = konto.getConsolidated(byCategory=byCategory, traceNames=['scatter'], fromDate=fromDate, categories=categories, toDate=toDate, accounts=accounts, thepattern=thepattern, categorySelection=categorySelection, sortScatterBy=sortScatterBy)
    return template('categorize.tpl', title=title, theX=theX, allcategoriesNames=consolidated['allcategoriesNames'], scatter=consolidated['scatter'], reverseSort=sortScatterByReverse)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'dev':
        print('using dev engine')
        run(app, host='0.0.0.0', port=8080)
    else:
        print('using cherrypy engine')
        run(app, server='cherrypy', host='0.0.0.0', port=8080)
