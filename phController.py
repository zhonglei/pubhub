'''

Pubhub's main controller logic for the interaction between the Pubhub database,
the Pubmed database and the front-end Bottle web server.

Created on Apr 26, 2014

@author: zhil2
'''

import MySQLdb
import urllib2
from bottle import template
from logging import warning, debug
import pprint
import time

from phTools import singleStrip, replaceKeyValuePair
from phInfo import phDbInfo, webServerInfo
from pubmedApi import PubmedApi
from phDatabaseApi import PhDatabase, MysqlConnection, constructMysqlDatetimeStr

'''
format '%(asctime)s %(name)s %(levelname)s: %(message)s'
level DEBUG, INFO
'''
# import logging
# logging.basicConfig(format='%(name)s %(levelname)s: %(message)s',
#                     level=logging.DEBUG)

def constructPubmedQueryList(phdb, subscriberIdIn = None):
    '''
    Return a list of Pubmed queries and their corresponding subscriberIds 
    based on information in the interest table of database phdb.
    
    If subscriberIdIn is not provided, construct a list for all subscribers;
    otherwise, the list is only for the subscriber specified.
    
    Rules to construct the list:
    1) All categorized as general_journal (category = 2) should be queried 
    with no specific keyword. e.g. Nature[Journal]
    2) All categorized as expert_journal (category = 3) should be queried 
    with keywords (category = 4) for a specific subscriber.
    e.g.: (telomerase) AND ("Nature"[Journal] OR "Nature medicine"[Journal] )    
                
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
    [(u'(biology OR medical OR neuroscience OR gene OR brain) AND ("Cell"[Journal])', [1L]), (u'(biology OR medical OR neuroscience OR gene OR brain) AND ("Nature"[Journal])', [1L, 2L]), (u'(biology OR medical OR neuroscience OR gene OR brain) AND ("Science"[Journal])', [1L, 2L]), (u'(telomerase and cancer biology) AND ("Cell"[Journal] OR "Nature"[Journal] OR "Science"[Journal] OR "Molecular and Cellular Biology"[Journal] OR "Molecular Cell"[Journal] OR "Nature structural and Molecular Biology"[Journal] )', [1L]), (u'(telomere and DNA replication) AND ("Cell"[Journal] OR "Nature"[Journal] OR "Science"[Journal] OR "Molecular and Cellular Biology"[Journal] OR "Molecular Cell"[Journal] OR "Nature structural and Molecular Biology"[Journal] )', [1L]), (u'(noncoding RNA) AND ("Nature"[Journal] OR "Science"[Journal] OR "Immunity"[Journal] OR "Journal of Immunology"[Journal] OR "Molecular Cell"[Journal] OR "Nature structural and Molecular Biology"[Journal] )', [2L])]
    >>> constructPubmedQueryList(phdb, 1L)
    [(u'(biology OR medical OR neuroscience OR gene OR brain) AND ("Cell"[Journal])', [1L]), (u'(biology OR medical OR neuroscience OR gene OR brain) AND ("Nature"[Journal])', [1L]), (u'(biology OR medical OR neuroscience OR gene OR brain) AND ("Science"[Journal])', [1L]), (u'(telomerase and cancer biology) AND ("Cell"[Journal] OR "Nature"[Journal] OR "Science"[Journal] OR "Molecular and Cellular Biology"[Journal] OR "Molecular Cell"[Journal] OR "Nature structural and Molecular Biology"[Journal] )', [1L]), (u'(telomere and DNA replication) AND ("Cell"[Journal] OR "Nature"[Journal] OR "Science"[Journal] OR "Molecular and Cellular Biology"[Journal] OR "Molecular Cell"[Journal] OR "Nature structural and Molecular Biology"[Journal] )', [1L])]
    >>> phdb.close()
    '''
    
    listQuery=[]
    
    if subscriberIdIn is None:
        _, generalJournals = phdb.selectDistinct('interest', ['phrase',], 
                                             'category = 2') #generalJournal
    else:
        _, generalJournals = phdb.selectDistinct('interest', ['phrase',], 
                                             'category = 2 and subscriberId = '
                                             + str(subscriberIdIn))
        
    generalJournals = singleStrip(generalJournals)    
        
    for j in generalJournals:
        
        query = ''

        'for biology-related field, add filter'
        query += r'(biology OR medical OR neuroscience OR gene OR brain) AND '
        
        query += r'("%s"[Journal])' % j
        
        if subscriberIdIn is None:
            _, subscribers = phdb.selectDistinct('interest',['subscriberId',], 
                                                 "phrase = '%s'" % j)
            subscribers = singleStrip(subscribers)
        else:
            subscribers = [subscriberIdIn,]
        
        debug('query: '+query)
        debug('subscribers: '+str(subscribers))
        
        listQuery.append((query, subscribers))
        
    'FIXME: can have less number of db queries'

    if subscriberIdIn is None:    
        _, subscriberIds = phdb.selectDistinct('interest', ['subscriberId',])
        subscriberIds = singleStrip(subscriberIds)    
    else:
        subscriberIds = [subscriberIdIn,]
       
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
            
            debug('query: '+query)

            subscribers = [i]
            listQuery.append((query, subscribers))
            
    debug('constructed Pubmed query list:\n'+ pprint.pformat(listQuery))
            
    return listQuery

def constructPubmedTimeStr(startTime, endTime):
    '''
    Example:
    >>> constructPubmedTimeStr(1398036175.4, 1399531966.5)
    '(2014/04/20[PDAT] : 2014/05/08[PDAT])'
    '''
    startT = time.strftime('%Y/%m/%d[PDAT]', time.gmtime(startTime))
    endT = time.strftime('%Y/%m/%d[PDAT]', time.gmtime(endTime))
    return '(' + startT + ' : ' + endT + ')'

def queryPubmedAndStoreResults(queryStartTime, queryEndTime, subscriberIdIn = None):
    '''
    If subscriberIdIn is not specified, query for all subscribers in database;
    otherwise, query for that specific subscriber only.
    
    Example:
    >>> from phInfo import testDbInfo
    >>> phdb = PhDatabase(MysqlConnection(testDbInfo['dbName'],testDbInfo['ip'],testDbInfo['user'],testDbInfo['password']))
    >>> phdb.formatDatabase()
    >>> subscriberId = signUpSubscriber('lizhi1981@gmail.com', 'Zhi', 'Li', '1', ['DNA sequencing'])
    >>> queryPubmedAndStoreResults(1399664864 - 2 * 24 * 3600, 1399664864, subscriberId)
    >>> _, res = phdb.selectDistinct('article',['articleId'])
    >>> print res
    >>>
    >>> phdb.close()
    '''    

    timeStr = constructPubmedTimeStr(queryStartTime, queryEndTime)

    'connect pubhub database'
    phdb = PhDatabase(MysqlConnection(phDbInfo['dbName'],phDbInfo['ip'],phDbInfo['user'],phDbInfo['password']))    
    
    res = constructPubmedQueryList(phdb, subscriberIdIn)
    
    for queryStr, listSubscriber in res:
        
        'add time constraint'
        queryStr += ' AND '+ timeStr
        
        'add type: journal article'
        #queryStr += ' AND (Journal Article[ptyp])'

        print 'query: '+queryStr
        print 'subscribers: '+str(listSubscriber)        
            
        'URL encoding'
        queryStr = urllib2.quote(queryStr.encode("ascii"))
        
        debug('query: \n\n'+queryStr+'\n')
        
        'query pubmed'
        pa = PubmedApi()
        ldArticle, ldAuthor = pa.query(queryStr, 100)
        
        for dArticle in ldArticle:
                                       
            'record article'
            dArticle['articleId'] = None #prepare to get LAST_INSERT_ID
            
            try:
                articleId = phdb.insertOneReturnLastInsertId('article', dArticle) 
            except MySQLdb.IntegrityError:
                'key duplication. already in database. try to select'
                _, articleId = phdb.selectDistinct('article',['articleId',],
                                                'PMID = '+dArticle['PMID'])                
                articleId = singleStrip(articleId)[0]
                
            if articleId == -1: #article insertion fails (could be already in db)
                continue
            
            for s in listSubscriber:
                                                                   
                'record subscriber_article'
                dSubscriber_article = {}
                dSubscriber_article['subscriber_articleId'] = None
                dSubscriber_article['subscriberId'] = s
                dSubscriber_article['articleId'] = articleId
                
                try:
                    subscriber_articleId = phdb.insertOneReturnLastInsertId(
                                        'subscriber_article', dSubscriber_article)
                except MySQLdb.IntegrityError:
                    continue
                
                'record subscriber_articleEvent'
                dSubscriber_articleEvent = {}
                dSubscriber_articleEvent['subscriber_articleId'] = subscriber_articleId
                dSubscriber_articleEvent['timestamp'] = constructMysqlDatetimeStr(time.time())
                dSubscriber_articleEvent['category'] = 1 #created
                dSubscriber_articleEvent['status'] = 1 #yes

                try:
                    phdb.insertOne('subscriber_articleEvent', dSubscriber_articleEvent)
                except MySQLdb.IntegrityError:
                    continue

        'record author'
        #ldAuthorForArticle = [l for l in ldAuthor if l['PMID']==dArticle['PMID']]
        replaceKeyValuePair(phdb, ldAuthor, 'article', 'PMID', 'articleId')
                                # Need to look up articleId in article, 
                                # and replace key PMID with articleID
        try:
            phdb.insertMany('author', ldAuthor)
        except MySQLdb.IntegrityError:
            pass
        
    '''lastly, if the operation for all subscribers instead of any individual
    subscriber, also update the record in phDatabaseUpdateEvent'''
    if subscriberIdIn is None:
        d = {}
        now = time.time()
        d['timestamp'] = constructMysqlDatetimeStr(now)
        phdb.insertOne('phDatabaseUpdateEvent',d)    
        
    'close pubhub database'
    phdb.close()
    
def getListArticlePage(subscriberId, startTime, endTime, displayType = 'web'):
    '''
    Note: startTime and endTime are both in epoch time.
    '''
    startTime = constructMysqlDatetimeStr(startTime)
    endTime = constructMysqlDatetimeStr(endTime)
    
    phdb = PhDatabase(MysqlConnection(phDbInfo['dbName'],phDbInfo['ip'],
                                      phDbInfo['user'],phDbInfo['password']))
    
    'FIXME: 4 tables join!'
    queryStartTime=time.time()
    _, res = phdb.fetchall(u'''SELECT DISTINCT article.articleId, ArticleTitle, 
    JournalISOAbbreviation, DateCreated, firstAuthor.authorId, firstAuthor.initials, 
    firstAuthor.lastName, firstAuthor.affiliation, lastAuthor.authorId, 
    lastAuthor.lastName, lastAuthor.affiliation, DoiId, PMID 
    FROM article 
    LEFT JOIN subscriber_article ON article.articleId = subscriber_article.articleId 
    LEFT JOIN firstAuthor ON article.articleId = firstAuthor.articleId 
    LEFT JOIN lastAuthor ON article.articleId = lastAuthor.articleId 
    WHERE subscriber_article.subscriberId = %s 
    AND article.DateCreated > '%s' 
    AND article.DateCreated < '%s'
    ;''' % (subscriberId, startTime, endTime))
    timeElapsed = time.time()-queryStartTime
    if timeElapsed > 0.1:
        warning("showListArticle 4 tables join takes %.2f sec!" % timeElapsed)
    
    phdb.close()
    
    rows=[]
    for (articleId, ArticleTitle, JournalTitle, DateCreated, firstAuthorId, 
    firstAuthorInitials, firstAuthorLastName, firstAuthorAffiliation, 
    lastAuthorId, lastAuthorLastName, lastAuthorAffiliation, DoiId, PMID) in res:
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
        if firstAuthorLastName and firstAuthorLastName != '':
            if firstAuthorId != lastAuthorId:
                authorField = firstAuthorLastName+' et al., '+lastAuthorLastName+' Lab'
            else:
                authorField = ''
                if firstAuthorInitials and firstAuthorInitials != '':
                    authorField += firstAuthorInitials+' '
                authorField += firstAuthorLastName
        else:
            authorField = ''
        rows.append((ArticleTitle, JournalTitle, dayStr, authorField, 
                                        affiliation, recordAndRedirectStr))
    
    output = template('views/listArticle', rows = rows, displayType = displayType)
    
    return output

def recordSubscriberArticle(subscriberId, articleId, header):
    
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
    
def signUpSubscriber(email, firstName, lastName, areaId, keywords):
    'Return: subscriberId'

    phdb = PhDatabase(MysqlConnection(phDbInfo['dbName'],phDbInfo['ip'],
                                      phDbInfo['user'],phDbInfo['password']))
    
    '====insert subscriber===='
    s={}
    s['subscriberId'] = None # prepare for return
    s['firstName'] = firstName
    s['lastName'] = lastName
    s['email'] = email
    try:
        subscriberId = phdb.insertOneReturnLastInsertId('subscriber',s)
    except MySQLdb.IntegrityError:
        subscriberId = -2 #FIXME: very ad hoc subscriberId is +ve if successful
        
    '====insert interest===='
    if subscriberId > 0: #subscriber inserted without error
        si=[]
        _, areaName = phdb.selectDistinct('area',['areaName'],'areaId = ' 
                                                                + str(areaId))
        areaName = singleStrip(areaName)[0] #double strip
        '==area=='
        a={}
        a['subscriberId'] = subscriberId
        a['category'] = '1' # area. FIXME: can do better
        a['phrase'] = areaName
        si.append(a)
        '==generalJournl=='
        _, listGeneralJournalTitle = phdb.fetchall('''
        SELECT DISTINCT journal.journalTitle FROM journal
        LEFT JOIN journal_area ON journal.journalId = journal_area.journalId
        WHERE journal_area.areaId = %s AND journal.isGeneral = 1
        ''' % str(areaId))
        listGeneralJournalTitle = singleStrip(listGeneralJournalTitle)
        for journalTitle in listGeneralJournalTitle:
            j={}
            j['subscriberId'] = subscriberId
            j['category'] = '2' #general journal. FIXME: can do better
            j['phrase'] = journalTitle
            si.append(j)
        '==expertJournal=='
        _, listExpertJournalTitle = phdb.fetchall('''
        SELECT DISTINCT journal.journalTitle FROM journal
        LEFT JOIN journal_area ON journal.journalId = journal_area.journalId
        WHERE journal_area.areaId = %s AND journal.isGeneral = 0
        ''' % str(areaId))
        listExpertJournalTitle = singleStrip(listExpertJournalTitle)
        for journalTitle in listExpertJournalTitle:
            j={}
            j['subscriberId'] = subscriberId
            j['category'] = '3' #expert journal. FIXME: can do better
            j['phrase'] = journalTitle
            si.append(j)
        '==keyword=='
        for keyword in keywords:
            k={}
            k['subscriberId'] = subscriberId
            k['category'] = '4' #keyword. FIXME: can do better
            k['phrase'] = keyword
            si.append(k)
    
        phdb.insertMany('interest',si)
         
    phdb.close()
    
    return subscriberId

def getSubscriberEmail(subscriberId):
    'Return email address'

    'look up subscriber email address'
    phdb = PhDatabase(MysqlConnection(phDbInfo['dbName'],phDbInfo['ip'],
                                      phDbInfo['user'],phDbInfo['password']))
    _, email = phdb.selectDistinct('subscriber', ['email'], 
                                      'subscriberId = '+str(subscriberId))
    email = singleStrip(email)[0]
    
    phdb.close()
    
    return email

def getLastPhDatabaseUpdateTime():
    'Return last Pubhub database time.'
    phdb = PhDatabase(MysqlConnection(phDbInfo['dbName'],phDbInfo['ip'],
                                      phDbInfo['user'],phDbInfo['password']))
    _, lastTime = phdb.fetchall('''SELECT UNIX_TIMESTAMP(timestamp) 
                                   FROM phDatabaseUpdateEvent
                                   ORDER BY timestamp DESC LIMIT 1''')
    if not lastTime:
        lastTime = None # No records
    else:
        lastTime = singleStrip(lastTime)[0]

    phdb.close()

    return lastTime
    
if __name__ == '__main__':

    import doctest
    print doctest.testmod()
         

    
    
    
    
    