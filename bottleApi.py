'''

API for Bottle framework.

Created on Apr 30, 2014

@author: zhil2
'''
from bottle import route, run, response, template, get, post, request, static_file
from databaseApi import PhDatabase, MysqlConnection
from phInfo import phDbInfo
from phTools import singleStrip
import logging
import time

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

@route('/hello')
def hello():
    return "<h1>Hello World!</h1>"

@route('/')
@route('/hello/<name>')
def greet(name = 'Stranger'):
    return template('<h1>Hello {{name}}, how are you?</h1>', name = name)
    
@route('/test')
def test():
    phdb = PhDatabase(MysqlConnection(phDbInfo['dbName'],phDbInfo['ip'],
                                      phDbInfo['user'],phDbInfo['password']))
    _, res = phdb.selectDistinct('article',['articleId','PMID','DoiId',
                                            'JournalTitle','ArticleTitle',])    
    phdb.close()
     
    output = template('views/test', rows = res)
    return output

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
    _, res = phdb.fetchall('''SELECT DISTINCT ArticleTitle, JournalISOAbbreviation, 
    DateCreated, firstAuthor.lastName, lastAuthor.lastName, firstAuthor.affiliation, 
    lastAuthor.affiliation, DoiId, PMID FROM article 
    LEFT JOIN subscriber_article ON article.articleId = subscriber_article.articleId 
    LEFT JOIN firstAuthor ON article.articleId = firstAuthor.articleId 
    LEFT JOIN lastAuthor ON article.articleId = lastAuthor.articleId 
    WHERE subscriber_article.subscriberId=1;''')
    timeElapsed = time.time()-queryStartTime
    if timeElapsed > 1:
        logging.warning("showListArticle 4 tables join takes %.2f sec!" % timeElapsed)
    
    phdb.close()
    
    rows=[]
    for ArticleTitle, JournalTitle, DateCreated, firstAuthorLastName, \
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
        if firstAuthorLastName != '':
            authorField = firstAuthorLastName+' et al., '+lastAuthorLastName+' Lab'
        else:
            authorField = ''
        rows.append((ArticleTitle, JournalTitle, dayStr, authorField, affiliation, www))
    
    output = template('views/listArticle', rows = rows)
    return output

@route('/add')
def addition():
    x = request.query.x
    y = request.query.y or 5
    return ("<h1>%d</h1>" % (int(x)+int(y)))


if __name__ == '__main__':
    import doctest
    print doctest.testmod()
    
    run(host = '0.0.0.0', port = 8080)



#     jsonRes = json.dumps(dbRes, indent = 2)
#     response.content_type = 'application/json'
#     return jsonRes

#from plotly import plotly

# py = plotly("pubhub", "sjt0boshh4")
# @get('/plot')
# def form():
#     return '''<h2>Graph via Plot.ly</h2>
#             <form method="POST" action="/plot">
#               Name: <input name="name1" type="text" />
#               Age: <input name="age1" type="text" /><br/>
#               Name: <input name="name2" type="text" />
#               Age: <input name="age2" type="text" /><br/>
#               Name: <input name="name3" type="text" />
#               Age: <input name="age3" type="text" /><br/>                
#               <input type="submit" />
#             </form>'''
# @post('/plot')
# def submit():
#     name1   = request.forms.get('name1')
#     age1    = request.forms.get('age1')
#     name2   = request.forms.get('name2')
#     age2    = request.forms.get('age2')
#     name3   = request.forms.get('name3')
#     age3    = request.forms.get('age3')
#     
#     x0 = [name1, name2, name3];
#     y0 = [age1, age2, age3];
#     data = {'x': x0, 'y': y0, 'type': 'bar'}
#     response = py.plot([data])
#     url = response['url']
#     filename = response['filename']
#     return template('<h1>Congrats!</h1><div>View your graph here: \
#       <a href=""</a></div>', url=url)

# @route('/new')
# def new(request):
#     '''                                                                                                            
#     Example:                                                                                                       
#     /new?subscriberId=1                                                                                            
#     '''
#     subscriberId = request.GET.get('subscriberId','0')
#     return "<h1> subscriberId = "+str(subscriberId)+". </h1>"


    
