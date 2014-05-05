'''

Methods for running the Bottle web server.

Created on Apr 30, 2014

@author: zhil2
'''
from bottle import route, run, request, static_file, redirect
#from bottle import response, get, post
from phDatabaseApi import PhDatabase, MysqlConnection, constructMysqlDatetimeStr
from phInfo import phDbInfo
from phTools import singleStrip
import logging
from logging import debug
import time
import sys
from phController import getListArticlePage

'''
format '%(asctime)s %(name)s %(levelname)s: %(message)s'
level DEBUG, INFO
'''
logging.basicConfig(format='%(name)s %(levelname)s: %(message)s',
                    level=logging.INFO)

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

    debug(header)
    
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
    
@route('/signup')
def signup():
    return '''
        <h1>You are invited to Scooply's alpha test!</h1>
        <form action="/signup" method="post">
        
            <h3>Sign up with your Stanford email address</h3>
            
            <p>
                Email: <input name="email" type="text" required />@stanford.edu <br>
                Password: <input name="password" type="password" required/>  <br>
                Confirm password: <input name="passwordAgain" type="password" required />  
            </p>

            <h3>Tell us a bit more about yourself</h3>

            <p>
                <b>What's your name?</b><br>
                First: <input name="firstName" type="text" /> Last: <input name="lastName" type="text" />
            </p>
            
            <p>
                <b>What's your primary research area?</b><br>
                <select name="area">
                    <option value="1">Bioinformatics and computational genomics</option>
                    <option value="2">Biophysics and bioengineering</option>
                    <option value="3">Developmental biology, stem cell biology and genetics</option>
                    <option value="4">Microbiology and immunology</option>
                    <option value="5">Biochemistry, cell biology and molecular biology</option>
                    <option value="6">Neurosciences</option>
                    <option value="7">Clinical sciences</option>
                </select> 
            </p>
            
            <p>
                <b>What specific research topics would you like to receive Scooply alerts on?</b> <br>
                <textarea name="keywords" rows="8" cols="50" required placeholder="For example: telomeres and telomerase, noncoding RNA, mechanisms of aging. Please type each topic in a separate line."></textarea>
            </p>
            
            <h3></h3>
            
            <p>
                <input value="Sign up" type="submit" /> <br>
                Already have an account? <a href="/signin">Sign in</a>
            </p>
            
        </form>
    '''
    '''
    <p>By clicking on Sign up, you agree to Scooply's terms & conditions 
    and privacy policy</p>
    '''

@route('/signup', method='POST')
def do_signup():
    email = request.forms.get('email')
    password = request.forms.get('password')
    passwordAgain = request.forms.get('passwordAgain')
    firstName = request.forms.get('firstName') or ""
    lastName = request.forms.get('lastName') or ""
    area = request.forms.get('area')
    keywords = request.forms.get('keywords')
    return ("<h3>Email: " + email + "</h3>"
            + "<h3>Password: " + password + "</h3>"
            + "<h3>Confirm password: "+ passwordAgain + "</h3>"
            + "<h3>First Name: "+ firstName + "</h3>"
            + "<h3>Last Name: "+ lastName + "</h3>"
            + "<h3>Area: "+ area + "</h3>"
            + "<h3>Keywords: "+ str(keywords) + "</h3>"
            )
    
@route('/signin')
def signin():
    return '<h1>Scooply sign in page placeholder.</h1>'

@route('/add')
def addition():
    x = request.query.x
    y = request.query.y or 5
    return ("<h1>%d</h1>" % (int(x)+int(y)))


if __name__ == '__main__':

    import doctest
    print doctest.testmod()
    
    'if with argument --doctest-only, skip the rest'
    if len(sys.argv) > 1:
        for a in sys.argv[1:]: 
            if a =='--doctest-only':
                sys.exit()
    
    run(host = '0.0.0.0', port = 8080)

