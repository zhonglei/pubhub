'''

API for Bottle framework.

Created on Apr 30, 2014

@author: zhil2
'''
from bottle import route, run, response, template, get, post, request, \
                   static_file, redirect
from databaseApi import PhDatabase, MysqlConnection, constructMysqlDatetimeStr
from phInfo import phDbInfo
from phTools import singleStrip
import logging
import time
import sys

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

@route('/listArticle')      #/listArticle?subscriberId=1
def showListArticle():
    subscriberId = request.query.subscriberId
    phdb = PhDatabase(MysqlConnection(phDbInfo['dbName'],phDbInfo['ip'],
                                      phDbInfo['user'],phDbInfo['password']))

#     _, articleRes = phdb.selectDistinct('article JOIN subscriber_article '+
#             'ON article.articleId = subscriber_article.articleId', 
#             ['ArticleTitle', 'JournalISOAbbreviation', 'DateCreated',],
#             'subscriber_article.subscriberId='+str(subscriberId)
#             )

    'FIXME: 4 tables join!'
    queryStartTime=time.time()
    _, res = phdb.fetchall('''SELECT DISTINCT article.articleId, ArticleTitle, JournalISOAbbreviation, 
    DateCreated, firstAuthor.lastName, lastAuthor.lastName, firstAuthor.affiliation, 
    lastAuthor.affiliation, DoiId, PMID FROM article 
    LEFT JOIN subscriber_article ON article.articleId = subscriber_article.articleId 
    LEFT JOIN firstAuthor ON article.articleId = firstAuthor.articleId 
    LEFT JOIN lastAuthor ON article.articleId = lastAuthor.articleId 
    WHERE subscriber_article.subscriberId = %s;''' % subscriberId)
    timeElapsed = time.time()-queryStartTime
    if timeElapsed > 1:
        logging.warning("showListArticle 4 tables join takes %.2f sec!" % timeElapsed)
    
    phdb.close()
    
    rows=[]
    for articleId, ArticleTitle, JournalTitle, DateCreated, firstAuthorLastName, \
    lastAuthorLastName, firstAuthorAffiliation, lastAuthorAffiliation, DoiId, PMID in res:
        daysElapsed = int((time.time()-int(DateCreated.strftime('%s')))/24/3600)
        if daysElapsed == 0:
            dayStr = 'Today'
        elif daysElapsed == 1:
            dayStr = '1 day ago'
        else:
            dayStr = '%d days ago' % daysElapsed
        affiliation=''
        if firstAuthorAffiliation != '':
            affiliation = firstAuthorAffiliation
        elif lastAuthorAffiliation != '':
            affiliation = lastAuthorAffiliation
        if DoiId != '':
            www = 'http://dx.doi.org/' + DoiId
        else: 
            www = 'http://www.ncbi.nlm.nih.gov/pubmed/' + str(PMID)
        recordAndRedirectStr = \
                    'redirect?subscriberId=%s&articleId=%ld&redirectUrl=%s' \
                    % (subscriberId,articleId,www)
        if firstAuthorLastName != '':
            authorField = firstAuthorLastName+' et al., '+lastAuthorLastName+' Lab'
        else:
            authorField = ''
        rows.append((ArticleTitle, JournalTitle, dayStr, authorField, 
                                        affiliation, recordAndRedirectStr))
    
    output = template('views/listArticle', rows = rows)
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

