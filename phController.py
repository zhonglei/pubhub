'''

Control logic of Pubhub.

Created on Apr 26, 2014

@author: zhil2
'''

from pubmedApi import PubmedApi
from phDatabaseApi import PhDatabase, MysqlConnection, constructMysqlDatetimeStr
import logging
from phTools import singleStrip
import pprint
import time
from phInfo import phDbInfo, webServerInfo
from bottle import template

logging.basicConfig(format='%(name)s %(levelname)s: %(message)s',
                    level=logging.INFO)

def replaceKeyValuePair(db, listDict, tableName, keyOld, keyNew):
    '''
    Replace a old key-value pair (with key keyOld) in a list of dictionaries 
    (listDict) with a new pair (with key keyNew), based on the old/new key 
    lookup in a database table (tableName). Commonly used because there are 
    many cases one needs to lookup and replace the id column of a table 
    based on another column (for example, look up and replace PMID with 
    articleId in table article).

    Example:
    >>> from phInfo import testDbInfo
    >>> phdb = PhDatabase(MysqlConnection(testDbInfo['dbName'],testDbInfo['ip'],testDbInfo['user'],testDbInfo['password']))
    >>> phdb.conn._execute('DELETE FROM Dict')
    0
    >>> phdb.insertMany('Dict',[{'k':'Zhi','v':'32'},{'k':'Hu','v':'28'},{'k':'Russ','v':'31'},{'k':'Lala','v':'31'},{'k':'Franklin','v':'31'},{'k':'Yang','v':'31'}])
    0
    >>> _,res = phdb.selectDistinct('Dict',['k','v'])
    >>> print res
    (('Zhi', '32'), ('Hu', '28'), ('Russ', '31'), ('Lala', '31'), ('Franklin', '31'), ('Yang', '31'))
    >>> ld = [{'k':'Zhi', 'x':'y'},{'k':'Franklin', 'z':'w'}]
    >>> replaceKeyValuePair(phdb, ld, 'Dict', 'k', 'v')
    0
    >>> ld
    [{'x': 'y', 'v': '32'}, {'z': 'w', 'v': '31'}]
    >>> phdb.close()    
    '''
    _, res = db.selectDistinct(tableName, [keyOld, keyNew])
    dictKeyOld2New = dict(map(str, x) for x in res) # map everything to string
    rf = 0
    for d in listDict:
        try:
            d[keyNew] = dictKeyOld2New[d[keyOld]]
            d.pop(keyOld,None)
        except Exception as e:
            logging.warning(e)
            rf = 1                
        logging.debug(d)
        
    return rf

def constructPubmedQueryList(phdb):
    '''
    Return a list of Pubmed queries and their corresponding subscriberIds 
    based on information in the interest table of database phdb.
    Rules to construct the list:
    1) All categorized as general_journal (category = 1) should be queried 
    with no specific keyword. e.g. Nature[Journal]
    2) All categorized as expert_journal (category = 2) should be queried 
    with keywords (category = 3) for a specific subscriber.
    e.g.: (telomerase) AND ("Nature"[Journal] OR "Nature medicine"[Journal] )    
    
    category: 0 - area, 1- general_journal, 2 - expert_journal, 3 - keyword, 
    4 - author
            
    Example:
    >>> from phInfo import testDbInfo
    >>> phdb = PhDatabase(MysqlConnection(testDbInfo['dbName'],testDbInfo['ip'],testDbInfo['user'],testDbInfo['password']))
    >>> phdb.conn._execute("DROP TABLE subscriber_articleEvent")
    0
    >>> phdb.conn._execute("DROP TABLE subscriber_article")
    0
    >>> phdb.conn._execute("DROP TABLE interest")
    0
    >>> phdb.conn._execute("DROP TABLE subscriber")
    0
    >>> phdb.createTableSubscriber()
    0
    >>> phdb.createTableInterest()
    0
    >>> phdb.createTableSubscriber_Article()
    0
    >>> phdb.createTableSubscriber_ArticleEvent()
    0
    >>> ldSubscriber = [
    ...                {'firstName':'Franklin', 'lastName':'Zhong', 'email':'franklin.zhong@gmail.com'}, 
    ...                {'firstName':'Zhi', 'lastName':'Li', 'email':'henrylee18@yahoo.com'}, 
    ...                ]
    >>> ldInterest = [
    ...             {'subscriberId':'1', 'category':'0', 'phrase':'biochemistry'}, 
    ...                {'subscriberId':'1', 'category':'1', 'phrase':'cell biology'}, 
    ...                {'subscriberId':'1', 'category':'2', 'phrase':'Nature'}, 
    ...                {'subscriberId':'1', 'category':'2', 'phrase':'Science'}, 
    ...                {'subscriberId':'1', 'category':'2', 'phrase':'Cell'}, 
    ...                {'subscriberId':'1', 'category':'3', 'phrase':'Molecular Cell'}, 
    ...                {'subscriberId':'1', 'category':'3', 'phrase':'Nature structural and Molecular Biology'}, 
    ...                {'subscriberId':'1', 'category':'3', 'phrase':'Molecular and Cellular Biology'}, 
    ...                {'subscriberId':'1', 'category':'4', 'phrase':'telomerase and cancer biology'}, 
    ...                {'subscriberId':'1', 'category':'4', 'phrase':'telomere and DNA replication'}, 
    ...                {'subscriberId':'2', 'category':'1', 'phrase':'biochemistry'}, 
    ...                {'subscriberId':'2', 'category':'1', 'phrase':'Immunology'}, 
    ...                {'subscriberId':'2', 'category':'2', 'phrase':'Nature'}, 
    ...                {'subscriberId':'2', 'category':'2', 'phrase':'Science'}, 
    ...                {'subscriberId':'2', 'category':'3', 'phrase':'Immunity'}, 
    ...                {'subscriberId':'2', 'category':'3', 'phrase':'Journal of Immunology'}, 
    ...                {'subscriberId':'2', 'category':'3', 'phrase':'Molecular Cell'}, 
    ...                {'subscriberId':'2', 'category':'3', 'phrase':'Nature structural and Molecular Biology'}, 
    ...                {'subscriberId':'2', 'category':'4', 'phrase':'noncoding RNA'}, 
    ...                ]
    >>> phdb.insertMany('subscriber', ldSubscriber)
    0
    >>> phdb.insertMany('interest', ldInterest)
    0
    >>> constructPubmedQueryList(phdb)
    [('("Cell"[Journal])', [1L]), ('("Nature"[Journal])', [1L, 2L]), ('("Science"[Journal])', [1L, 2L]), ('(telomerase and cancer biology) AND ("Cell"[Journal] OR "Nature"[Journal] OR "Science"[Journal] OR "Molecular and Cellular Biology"[Journal] OR "Molecular Cell"[Journal] OR "Nature structural and Molecular Biology"[Journal] )', [1L]), ('(telomere and DNA replication) AND ("Cell"[Journal] OR "Nature"[Journal] OR "Science"[Journal] OR "Molecular and Cellular Biology"[Journal] OR "Molecular Cell"[Journal] OR "Nature structural and Molecular Biology"[Journal] )', [1L]), ('(noncoding RNA) AND ("Nature"[Journal] OR "Science"[Journal] OR "Immunity"[Journal] OR "Journal of Immunology"[Journal] OR "Molecular Cell"[Journal] OR "Nature structural and Molecular Biology"[Journal] )', [2L])]
    >>> phdb.close()
    '''
    
    listQuery=[]
    
    _, generalJournals = phdb.selectDistinct('interest', ['phrase',], 
                                             'category = 2') #generalJournal
    generalJournals = singleStrip(generalJournals)    
        
    for j in generalJournals:
        query = r'("%s"[Journal])' % j
        
        _, subscribers = phdb.selectDistinct('interest',['subscriberId',], 
                                             "phrase = '%s'" % j)
        subscribers = singleStrip(subscribers)
        
        logging.debug('query: '+query)
        logging.debug('subscribers: '+str(subscribers))
        
        listQuery.append((query, subscribers))
        
    'FIXME: can have less number of db queries'
    
    _, subscriberIds = phdb.selectDistinct('interest', ['subscriberId',])
    subscriberIds = singleStrip(subscriberIds)    
       
    for i in subscriberIds:
        
        _, keywords = phdb.selectDistinct('interest', ['phrase'], 
                                'subscriberId = %d AND category = 4' % i) #keyword
        keywords = singleStrip(keywords)
        
        _, subscriberGeneralJournals = phdb.selectDistinct('interest', 
                    ['phrase',], 'subscriberId = %d AND category = 2' % i) #generalJournal
        subscriberGeneralJournals = singleStrip(subscriberGeneralJournals)
        
        _, subscriberExpertJournals = phdb.selectDistinct('interest', 
                    ['phrase',], 'subscriberId = %d AND category = 3' % i) #expertJournal
        subscriberExpertJournals = singleStrip(subscriberExpertJournals)
        
        subscriberJournals = subscriberGeneralJournals + subscriberExpertJournals
        
        for k in keywords:
            query = r"(%s) AND (" % k
            for j in subscriberJournals[:-1]:
                query += r'"%s"[Journal] OR ' % j
            query += r'"%s"[Journal] )' % subscriberJournals[-1]
            
            logging.debug('query: '+query)

            subscribers = [i]
            listQuery.append((query, subscribers))
            
    logging.debug('constructed Pubmed query list:\n'+ pprint.pformat(listQuery))
            
    return listQuery

def constructPubmedTimeStr(t):
    '''
    Example:
    >>> constructPubmedTimeStr(1398036175.4)
    '(2014/04/20[PDAT] : 3000/01/01[PDAT])'
    '''
    return time.strftime('(%Y/%m/%d[PDAT] : 3000/01/01[PDAT])', time.gmtime(t))

def queryPubmedAndStoreResults(lastQueryTime):

    timeStr = constructPubmedTimeStr(lastQueryTime)

    'connect pubhub database'
    phdb = PhDatabase(MysqlConnection(phDbInfo['dbName'],phDbInfo['ip'],phDbInfo['user'],phDbInfo['password']))    
    
    res = constructPubmedQueryList(phdb)
    for queryStr, listSubscriber in res:
        
        'add time constraint'
        queryStr += ' AND '+ timeStr
        
        'add type: journal article'
        queryStr += ' AND (Journal Article[ptyp])'
            
        'replace space with +'
        queryStr = queryStr.replace(' ', '+')
        
        logging.info('query: \n\n'+queryStr+'\n')
        
        'query pubmed'
        pa = PubmedApi()
        ldArticle, ldAuthor = pa.query(queryStr, 100)
        
        for dArticle in ldArticle:
                                       
            'record article'
            dArticle['articleId'] = None #prepare to get LAST_INSERT_ID
            articleId = phdb.insertOneReturnLastInsertId('article', dArticle) 
            
            if articleId == -1: #article insertion fails (could be already in db)
                continue
            
            for s in listSubscriber:
                                                                   
                'record subscriber_article'
                dSubscriber_article = {}
                dSubscriber_article['subscriber_articleId'] = None
                dSubscriber_article['subscriberId'] = s
                dSubscriber_article['articleId'] = articleId
                
                subscriber_articleId = phdb.insertOneReturnLastInsertId(
                                    'subscriber_article', dSubscriber_article)
                
                'record subscriber_articleEvent'
                dSubscriber_articleEvent = {}
                dSubscriber_articleEvent['subscriber_articleId'] = subscriber_articleId
                dSubscriber_articleEvent['timestamp'] = constructMysqlDatetimeStr(time.time())
                dSubscriber_articleEvent['category'] = 1 #created
                dSubscriber_articleEvent['status'] = 1 #yes

                phdb.insertOne('subscriber_articleEvent', dSubscriber_articleEvent)

        'record author'
        #ldAuthorForArticle = [l for l in ldAuthor if l['PMID']==dArticle['PMID']]
        replaceKeyValuePair(phdb, ldAuthor, 'article', 'PMID', 'articleId')
                                # Need to look up articleId in article, 
                                # and replace key PMID with articleID
        phdb.insertMany('author', ldAuthor)
            
    'close pubhub database'
    phdb.close()
    
def getListArticlePage(subscriberId, sinceDaysAgo, displayType = 'web'):
    
    phdb = PhDatabase(MysqlConnection(phDbInfo['dbName'],phDbInfo['ip'],
                                      phDbInfo['user'],phDbInfo['password']))
    
    'FIXME: 4 tables join!'
    queryStartTime=time.time()
    _, res = phdb.fetchall('''SELECT DISTINCT article.articleId, ArticleTitle, JournalISOAbbreviation, 
    DateCreated, firstAuthor.lastName, lastAuthor.lastName, firstAuthor.affiliation, 
    lastAuthor.affiliation, DoiId, PMID FROM article 
    LEFT JOIN subscriber_article ON article.articleId = subscriber_article.articleId 
    LEFT JOIN firstAuthor ON article.articleId = firstAuthor.articleId 
    LEFT JOIN lastAuthor ON article.articleId = lastAuthor.articleId 
    WHERE subscriber_article.subscriberId = %s AND DATE_SUB(NOW(), Interval %d day) 
    < article.DateCreated;''' % (subscriberId,sinceDaysAgo))
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
        recordAndRedirectStr = 'http://'+webServerInfo['addr']+ '/' \
                    'redirect?subscriberId=%s&articleId=%ld&redirectUrl=%s' \
                    % (subscriberId,articleId,www)
        if firstAuthorLastName != '':
            authorField = firstAuthorLastName+' et al., '+lastAuthorLastName+' Lab'
        else:
            authorField = ''
        rows.append((ArticleTitle, JournalTitle, dayStr, authorField, 
                                        affiliation, recordAndRedirectStr))
    
    output = template('views/listArticle', rows = rows, displayType = displayType)
    
    return output
    
if __name__ == '__main__':

    import doctest
    print doctest.testmod()
         

    
    
    
    
    