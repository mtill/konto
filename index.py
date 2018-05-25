#!/usr/bin/env python3
# coding=utf-8

from bottle import Bottle, static_file, request, template, run
import time
import json
import sys

import kontomodel as konto

app = Bottle()

@app.route('/')
@app.route('/byCategory/<byCategory>')
def indexFile(byCategory='month'):
    lists = konto.getLists()
    return template('index.tpl', title='Ausgaben', site=byCategory, options=lists, byCategory=byCategory, tracesJSON=json.dumps(['traces', 'profit']))

@app.route('/profit')
def profit():
    lists = konto.getLists()
    return template('index.tpl', title='Gewinn', site='profit', options=lists, byCategory='month', tracesJSON=json.dumps(['profit', 'totalprofit']))

@app.route('/static/<thefilename:path>')
def server_static(thefilename):
    return static_file(thefilename, root='static')

@app.route('/editCategories', method='GET')
def editCategories(thefilename='categories'):
    categories = konto.readCategoriesFile()
    uncategorized = konto.getUncategorizedItems()
    return template('editCategories.tpl', categories=categories, uncategorized=uncategorized)

@app.route('/editCategories', method='POST')
def submitCategories():
    konto.writeCategories(categoriesString=request.forms.getunicode('categories'))
    return editCategories()

@app.route('/getConsolidated', method="POST")
def getConsolidated():
    categories = konto.parseCategories()
    byCategory = request.json.get('byCategory')
    traces = request.json.get('traces')

    fromDateJSON = request.json.get('fromDate', None)
    fromDate = None
    if fromDateJSON is not None:
        fromDate = time.strptime(fromDateJSON, '%Y-%m-%d')

    toDateJSON = request.json.get('toDate', None)
    toDate = None
    if toDateJSON is not None:
        toDate = time.strptime(toDateJSON, '%Y-%m-%d')

    consolidated = konto.getConsolidated(byCategory=byCategory, traceNames=traces, fromDate=fromDate, categories=categories, toDate=toDate)

    # return json.dumps(request.json.get('items'))
    return json.dumps({'traces': consolidated['traces'], 'foundDuplicates': consolidated['foundDuplicates']})

@app.route('/categorize', method="POST")
def categorize():
    itemId = request.json.get('itemId')
    thecategory = request.json.get('thecategory')
    konto.updateCategory(itemId=itemId, thecategory=thecategory)

@app.route('/getDetails', method="POST")
def getDetails():
    theX = request.json.get('theX')
    categories = konto.parseCategories()
    byCategory = request.json.get('byCategory')

    fromDateJSON = request.json.get('fromDate', None)
    fromDate = None
    if fromDateJSON is not None:
        fromDate = time.strptime(fromDateJSON, '%Y-%m-%d')

    toDateJSON = request.json.get('toDate', None)
    toDate = None
    if toDateJSON is not None:
        toDate = time.strptime(toDateJSON, '%Y-%m-%d')

    consolidated = konto.getConsolidated(byCategory=byCategory, traceNames=['scatter'], fromDate=fromDate, categories=categories, toDate=toDate)

    return template('categorize.tpl', title=template("Umsätze für {{theX}}", theX=theX), theX=theX, scatter=consolidated['scatter'])

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'dev':
        print('using dev engine')
        run(app, host='0.0.0.0', port=8080)
    else:
        print('using cherrypy engine')
        run(app, server='cherrypy', host='0.0.0.0', port=8080)
