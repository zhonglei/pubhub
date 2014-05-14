'''

Methods for running the Bottle web server.

Created on Apr 30, 2014

@author: zhil2
'''

from bottle import route, run, request, static_file, redirect, template, response
#from bottle import get, post
from logging import debug
import sys
import time

from phInfo import phDbInfo, pubmedBacktrackSecondForNewSubscriber, webServerInfo
from phDatabaseApi import Subscriber_ArticleEventCategory, dbBoolean
from phController import getListArticlePage, recordSubscriberArticle, \
                         signUpSubscriber, queryPubmedAndStoreResults, \
                         getArticleMorePage, getListArticleInTimeInterval, \
                         getListPinnedArticle, verifyPasswordAndGetSubscriberId, \
                         getSubscriberIdInCookie, deleteSubscriberIdInCookie, \
                         setSubscriberIdInCookie
'''
format '%(asctime)s %(name)s %(levelname)s: %(message)s'
level DEBUG, INFO
'''
# import logging
# logging.basicConfig(format='%(name)s %(levelname)s: %(message)s',
#                     level=logging.DEBUG)

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

@route('/listArticle')
def showListArticle():
    '''
    /listArticle?subscriberId=1&sinceDaysAgo=10
    '''
    subscriberId = request.query.subscriberId
    sinceDaysAgo = request.query.sinceDaysAgo or '7'
    sinceDaysAgo = int(sinceDaysAgo)
    now = time.time()
    startTime = now - sinceDaysAgo * 24 * 3600
    endTime = now

    listArticleId = getListArticleInTimeInterval(phDbInfo, startTime, endTime, subscriberId)
    output = getListArticlePage(phDbInfo, webServerInfo, listArticleId, subscriberId)

    return output

@route('/redirect') 
def recordSubscriberArticleAndRedirect():
    '''
    /redirect?subscriberId=1&articleId=2&redirectUrl=http://www.google.com
    '''
    subscriberId = request.query.subscriberId
    articleId = request.query.articleId
    redirectUrl = request.query.redirectUrl
    
    'parse request header info'
    header = ""
    headerFields = request.headers.keys()
    for field in headerFields:
        header += str(field) + " | " + str(request.get_header(field)) + " || "
    debug(header)

    extraInfo = header
    extraInfo += 'redirectUrl' + " | " + redirectUrl + " || "
    
    'record event'
    category = Subscriber_ArticleEventCategory.extlinkClicked
    status = dbBoolean.yes
    recordSubscriberArticle(phDbInfo, subscriberId, articleId, 
                                    extraInfo, category, status)
        
    'redirect'
    redirect(redirectUrl)

@route('/articleMore')
def showArticleMore():
    '''
    /articleMore?subscriberId=1&articleId=2
    '''
    subscriberId = request.query.subscriberId
    articleId = request.query.articleId

    'parse request header info'
    header = ""
    headerFields = request.headers.keys()
    for field in headerFields:
        header += str(field) + " | " + str(request.get_header(field)) + " || "
    debug(header)
    
    extraInfo = header
    
    'record event'
    recordSubscriberArticle(phDbInfo, subscriberId, articleId, extraInfo, 
                            Subscriber_ArticleEventCategory.moreClicked,
                            dbBoolean.yes)
    
    'display articleMore page'
    output = getArticleMorePage(phDbInfo, subscriberId, articleId)
    return output
        
@route('/pin')
def pinArticle():
    '''
    /pin?subscriberId=1&articleId=2&status=0 
    '''
    subscriberId = request.query.subscriberId
    articleId = request.query.articleId
    status = request.query.status
    
    'parse request header info'
    header = ""
    headerFields = request.headers.keys()
    for field in headerFields:
        header += str(field) + " | " + str(request.get_header(field)) + " || "
    debug(header)
    
    extraInfo = header  
      
    '1) update pin status'
    category = Subscriber_ArticleEventCategory.pinned
    recordSubscriberArticle(phDbInfo, subscriberId, articleId, extraInfo, 
                            category, status)

    '2) display articleMore page'
    output = getArticleMorePage(phDbInfo, subscriberId, articleId)
    
    return output

@route('/listPinnedArticle')
def showListPinnedArticle():
    '''
    /listPinnedArticle?subscriberId=1
    '''
    subscriberId = request.query.subscriberId

    listArticleId = getListPinnedArticle(phDbInfo, subscriberId)
    output = getListArticlePage(phDbInfo, webServerInfo, listArticleId, subscriberId, displayType = 'pinned')

    return output

    return 0

@route('/')
def root():
    subscriberId = getSubscriberIdInCookie(webServerInfo)

    if subscriberId:
        listArticlePageUrl = 'listArticle?subscriberId=%s' % str(subscriberId)
        output = (r'Welcome to Scooply! You have already signed in. Start exploring <a href="%s">here</a>.' +
                  r' Or <a href="/signout">sign out</a>.') % listArticlePageUrl
    else:
        output = (r'Welcome to Scooply! <a href="/signin">Sign in</a> or ' +
                  r'<a href="/signup">sign up</a>.')
        
    return output
        
@route('/signup')
@route('/register')
def signup():    
    subscriberId = getSubscriberIdInCookie(webServerInfo)

    if subscriberId:
        listArticlePageUrl = 'listArticle?subscriberId=%s' % str(subscriberId)
        output = r'You have already signed in. <a href="/signout">Sign out</a> first.' \
               + r' Or start exploring <a href="%s">here</a>.' % listArticlePageUrl
        return output

    return template('views/signup')

@route('/signup', method='POST')
def do_signup():
    email = request.forms.get('email')
    email += '@stanford.edu'    
    password = request.forms.get('password')
    firstName = request.forms.get('firstName') or ""
    lastName = request.forms.get('lastName') or ""
    areaId = request.forms.get('areaId')
    keywords = request.forms.get('keywords')
    keywords = keywords.split('\r\n')
    
    '====sign up===='
    subscriberId = signUpSubscriber(phDbInfo, email, password, firstName, lastName, areaId, keywords)

    '====query Pubmed for new subscriber===='
    now = time.time()
    queryStartTime = now - pubmedBacktrackSecondForNewSubscriber
    queryEndTime = now
    queryPubmedAndStoreResults(phDbInfo, queryStartTime, queryEndTime, subscriberId)
     
    '====return===='
    if subscriberId == -1:
        return (r'Oops... Looks like there are some issues. ' +
                r'<a href="/signup">Try again</a>.')
    elif subscriberId == -2:
        return (r'Oops... Looks like this email has already been used. ' +
                r'<a href="/signup">Try again</a> with a new one.')
    else:
        setSubscriberIdInCookie(webServerInfo, subscriberId)
        listArticlePageUrl = 'listArticle?subscriberId=%s' % str(subscriberId)
        return (r'You have successfully sign up! Now start exploring ' +
                r'<a href="%s">here</a>.') % listArticlePageUrl

@route('/signin')
@route('/login')
def signin():
    subscriberId = getSubscriberIdInCookie(webServerInfo)
    
    if subscriberId:
        listArticlePageUrl = 'listArticle?subscriberId=%s' % str(subscriberId)
        output = (r'You have already signed in. Start exploring <a href="%s">here</a>.' +
                  r' Or <a href="/signout">sign out</a>.') % listArticlePageUrl
        return output
     
    return template('views/signin')

@route('/signin', method='POST')
def do_signin():
    email = request.forms.get('email')
    email += '@stanford.edu'    
    password = request.forms.get('password')
    
    verified, subscriberId = verifyPasswordAndGetSubscriberId(phDbInfo, 
                                                              email, password)
    if not verified:
        return r'Either email or password is incorrect. <a href="/signin">Try again</a>.'        
        #redirect('/signin')
    else:
        setSubscriberIdInCookie(webServerInfo, subscriberId)
        listArticlePageUrl = 'listArticle?subscriberId=%s' % str(subscriberId)
        return r'You have signed in! Now start exploring <a href="%s">here</a>.' \
                                                            % listArticlePageUrl
        #redirect(listArticlePageUrl)

@route('/signout')
@route('/logout')
@route('/signoff')
def signout():    
    deleteSubscriberIdInCookie(webServerInfo)
    output = (r'You have signed out. <a href="/signin">Sign in</a> or ' +
              r'<a href="/signup">sign up</a>.')
    return output

@route('/artandilab')
def artandilab():
    redirect('/listArticle?subscriberId=1')
    
@route('/changlab')
def changlab():
    redirect('/listArticle?subscriberId=2')

if __name__ == '__main__':

    import doctest
    print doctest.testmod()

    'if with argument --doctest-only, skip the rest'
    if len(sys.argv) > 1:
        for a in sys.argv[1:]: 
            if a =='--doctest-only':
                sys.exit()
    
    run(host = '0.0.0.0', port = 8080)

