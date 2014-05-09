'''

Methods for running the Bottle web server.

Created on Apr 30, 2014

@author: zhil2
'''

from bottle import route, run, request, static_file, redirect, template
#from bottle import response, get, post
from logging import debug
import sys

from phController import getListArticlePage, \
                         recordSubscriberArticle, signUpSubscriber

'''
format '%(asctime)s %(name)s %(levelname)s: %(message)s'
level DEBUG, INFO
'''
# import logging
# logging.basicConfig(format='%(name)s %(levelname)s: %(message)s',
#                     level=logging.DEBUG)

@route('/')
def greet():
    return '<h1>Scooply main page placeholder.</h1>'

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
    subscriberId = request.query.subscriberId or ''
    sinceDaysAgo = request.query.sinceDaysAgo or '7'    
    output = getListArticlePage(subscriberId, int(sinceDaysAgo))
    return output

@route('/redirect') #/redirect?subscriberId=1&articleId=2&redirectUrl=http://www.google.com
def recordSubscriberArticleAndRedirect():
    subscriberId = request.query.subscriberId
    articleId = request.query.articleId
    redirectUrl = request.query.redirectUrl

    header = ""
    headerFields = request.headers.keys()
    for field in headerFields:
        header += str(field) + " | " + str(request.get_header(field)) + " || "
    debug(header)
    
    recordSubscriberArticle(subscriberId, articleId, header)
        
    redirect(redirectUrl)
    
@route('/signup')
def signup():
    output = template('views/signup')
    return output

@route('/signup', method='POST')
def do_signup():
    email = request.forms.get('email')
    email += '@stanford.edu'    
    #password = request.forms.get('password')
    #passwordAgain = request.forms.get('passwordAgain')
    firstName = request.forms.get('firstName') or ""
    lastName = request.forms.get('lastName') or ""
    areaId = request.forms.get('areaId')
    keywords = request.forms.get('keywords')
    keywords = keywords.split('\r\n')
    
    subscriberId = signUpSubscriber(email, firstName, lastName, areaId, keywords)
     
    '====return===='
    if subscriberId == -1:
        retMsg = "<h1>Oops... Looks like there are some issues.</h1>"
    elif subscriberId == -2:
        retMsg = "<h1>Oops... Looks like this email is already registered." \
                +" Try to use a new one.</h1>"
    else:
        retMsg = "<h1>Congrats! You've signed up to Scoooply.</h1>"
    
    return retMsg

'secret convenience function'
''
@route('/subscribe')
def subscribe():
    email = request.query.email
    firstName = request.query.firstName or ''
    lastName = request.query.lastName or ''
    areaId = request.query.areaId
    keywords = request.query.keywords
    keywords = keywords.split('\r\n')
    subscriberId = signUpSubscriber(email, firstName, lastName, areaId, keywords)
    if subscriberId == -1:
        retMsg = "<h1>Subscription fails for unknown reason.</h1>"
    elif subscriberId == -2:
        retMsg = "<h1>Subscription fails. Use a different email address.</h1>"
    else:
        retMsg = "<h1>Subscription succeeds.</h1>"
    return retMsg
    
@route('/signin')
def signin():
    return '<h1>Scooply sign in page placeholder.</h1>'

@route('/artandilab')
def artandilab():
    redirect('/listArticle?subscriberId=1&sinceDaysAgo=7')
    
@route('/changlab')
def changlab():
    redirect('/listArticle?subscriberId=2&sinceDaysAgo=7')

if __name__ == '__main__':

    import doctest
    print doctest.testmod()
    
    'if with argument --doctest-only, skip the rest'
    if len(sys.argv) > 1:
        for a in sys.argv[1:]: 
            if a =='--doctest-only':
                sys.exit()
    
    run(host = '0.0.0.0', port = 8080)

