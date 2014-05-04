'''

API for Bottle framework.

Created on Apr 30, 2014

@author: zhil2
'''
from bottle import route, run, request, static_file, redirect
#from bottle import response, get, post
from phDatabaseApi import PhDatabase, MysqlConnection, constructMysqlDatetimeStr
from phInfo import phDbInfo
from phTools import singleStrip
import logging
import time
import sys
from phController import getListArticlePage

logging.basicConfig(format='%(name)s %(levelname)s: %(message)s',
                    level=logging.DEBUG)

@route('/')
def greet():
    return '<h2>Welcome to sCoopLy -- the ONE place for bioscientists to keep track of latest research findings!</h2>'

@route('/css/<filepath:path>')
def serverStaticCss(filepath):
    return static_file(filepath, root='static/css')

@route('/fonts/<filepath:path>')
def serverStaticFonts(filepath):
    return static_file(filepath, root='static/fonts')

@route('/js/<filepath:path>')
def serverStaticJs(filepath):
    return static_file(filepath, root='static/js')

@route('/jasny-bootstrap/<filepath:path>')
def serverStaticJasny(filepath):
    return static_file(filepath, root='static/jasny-bootstrap')

@route('/listArticle')      #/listArticle?subscriberId=1&sinceDaysAgo=10
def showListArticle():
    subscriberId = request.query.subscriberId
    sinceDaysAgo = int(request.query.sinceDaysAgo) or 7    
    output = getListArticlePage(subscriberId, sinceDaysAgo)
    return output

@route('/redirect')     #/redirect?subscriberId=1&articleId=2&redirectUrl=http://www.google.com
def recordSubscriberArticleAndredirect():
    subscriberId = request.query.subscriberId
    articleId = request.query.articleId
    redirectUrl = request.query.redirectUrl

    header = ""
    headerFields = request.headers.keys()
    for field in headerFields:
        header += str(field) + " | " + str(request.get_header(field)) + " || "

    logging.debug(header)
    
    phdb = PhDatabase(MysqlConnection(phDbInfo['dbName'],phDbInfo['ip'],
                                      phDbInfo['user'],phDbInfo['password']))
    'record'
    _, s_aId = phdb.selectDistinct('subscriber_article',['subscriber_articleId'],
                                 'subscriberId = %s AND articleId = %s' %
                                 (subscriberId, articleId))
    
    s_aId = singleStrip(s_aId)[0] # need double strip
    
    s_aEventDict={}
    s_aEventDict['subscriber_articleId'] = s_aId
    s_aEventDict['timestamp'] = constructMysqlDatetimeStr(time.time())
    s_aEventDict['category'] = 4 #extlinkClicked
    s_aEventDict['status'] = 1 #yes
    s_aEventDict['requestHeader'] = header
    phdb.insertOne('subscriber_articleEvent',s_aEventDict)

    phdb.close()
    
    redirect(redirectUrl)
    

@route('/add')
def addition():
    x = request.query.x
    y = request.query.y or 5
    return ("<h1>%d</h1>" % (int(x)+int(y)))


if __name__ == '__main__':

    import doctest
    print doctest.testmod()
    
    'if with argument --doctest-only, do not start server'
    if len(sys.argv) > 1:
        for a in sys.argv[1:]: 
            if a =='--doctest-only':
                sys.exit()
    
    run(host = '0.0.0.0', port = 8080)

