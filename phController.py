'''

Control logic of Pubhub.

Created on Apr 26, 2014

@author: zhil2
'''

from pubmedApi import PubmedApi
from databaseApi import PhDatabase, MysqlConnection
import logging
from phTools import singleStrip
import pprint
import time

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
    >>> phdb = PhDatabase(MysqlConnection('testdb','54.187.112.65','root','lymanDelmedio123'))
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
    >>> phdb = PhDatabase(MysqlConnection('testdb','54.187.112.65','root','lymanDelmedio123'))
    >>> phdb.conn._execute("DROP TABLE interest")
    0
    >>> phdb.conn._execute("DROP TABLE subscriber")
    0
    >>> phdb.createTableSubscriber()
    0
    >>> phdb.createTableInterest()
    0
    >>> ldSubscriber = [
    ...                {'firstName':'Franklin', 'lastName':'Zhong', 'email':'franklin.zhong@gmail.com'}, 
    ...                {'firstName':'Zhi', 'lastName':'Li', 'email':'henrylee18@yahoo.com'}, 
    ...                ]
    >>> ldInterest = [
    ...             {'subscriberId':'1', 'category':'0', 'phrase':'biochemistry'}, 
    ...                {'subscriberId':'1', 'category':'0', 'phrase':'cell biology'}, 
    ...                {'subscriberId':'1', 'category':'1', 'phrase':'Nature'}, 
    ...                {'subscriberId':'1', 'category':'1', 'phrase':'Science'}, 
    ...                {'subscriberId':'1', 'category':'1', 'phrase':'Cell'}, 
    ...                {'subscriberId':'1', 'category':'2', 'phrase':'Molecular Cell'}, 
    ...                {'subscriberId':'1', 'category':'2', 'phrase':'Nature structural and Molecular Biology'}, 
    ...                {'subscriberId':'1', 'category':'2', 'phrase':'Molecular and Cellular Biology'}, 
    ...                {'subscriberId':'1', 'category':'3', 'phrase':'telomerase and cancer biology'}, 
    ...                {'subscriberId':'1', 'category':'3', 'phrase':'telomere and DNA replication'}, 
    ...                {'subscriberId':'2', 'category':'0', 'phrase':'biochemistry'}, 
    ...                {'subscriberId':'2', 'category':'0', 'phrase':'Immunology'}, 
    ...                {'subscriberId':'2', 'category':'1', 'phrase':'Nature'}, 
    ...                {'subscriberId':'2', 'category':'1', 'phrase':'Science'}, 
    ...                {'subscriberId':'2', 'category':'2', 'phrase':'Immunity'}, 
    ...                {'subscriberId':'2', 'category':'2', 'phrase':'Journal of Immunology'}, 
    ...                {'subscriberId':'2', 'category':'2', 'phrase':'Molecular Cell'}, 
    ...                {'subscriberId':'2', 'category':'2', 'phrase':'Nature structural and Molecular Biology'}, 
    ...                {'subscriberId':'2', 'category':'3', 'phrase':'noncoding RNA'}, 
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
                                             'category = 1')
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
                                'subscriberId = %d AND category = 3' % i)
        keywords = singleStrip(keywords)
        
        _, subscriberGeneralJournals = phdb.selectDistinct('interest', 
                    ['phrase',], 'subscriberId = %d AND category = 1' % i)
        subscriberGeneralJournals = singleStrip(subscriberGeneralJournals)
        
        _, subscriberExpertJournals = phdb.selectDistinct('interest', 
                    ['phrase',], 'subscriberId = %d AND category = 2' % i)
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

def constructPubmedTimeStr(lastQueryTime):
    '''
    Example:
    >>> constructPubmedTimeStr(1398036175.4)
    '(2014/04/20[PDAT] : 3000/01/01[PDAT])'
    '''
    return time.strftime('(%Y/%m/%d[PDAT] : 3000/01/01[PDAT])', time.gmtime(lastQueryTime))

def queryPubmedAndStoreResults(lastQueryTime):

    timeStr = constructPubmedTimeStr(lastQueryTime)

    'connect pubhub database'
    phdb = PhDatabase(MysqlConnection('pubhub', '54.187.112.65', 'root', 'lymanDelmedio123'))    
    
    res = constructPubmedQueryList(phdb)
    for queryStr, listSubscriber in res:
        
        'add time constraint'
        queryStr += ' AND '+ timeStr
        
        'add type: journal article'
        queryStr += ' AND Journal Article[ptyp]'
            
        'replace space with +'
        queryStr = queryStr.replace(' ', '+')
        
        logging.info('query: \n\n'+queryStr+'\n')
        
        'query pubmed'
        pa = PubmedApi()
        ldArticle, ldAuthor = pa.query(queryStr, 100)
               
        'record article'
        phdb.insertMany('article', ldArticle)
       
        'record author'
        replaceKeyValuePair(phdb, ldAuthor, 'article', 'PMID', 'articleId')
                                # Need to look up articleId in article, 
                                # and replace key PMID with articleID
        phdb.insertMany('author', ldAuthor)
      
    'close pubhub database'
    phdb.close()
    
    pass
    

if __name__ == '__main__':
    
    '================================'
    'create subscriber query'
    '================================'
     
#      
#     'create tables and populate dummy subscribers'
#     '''
#     subscriber:    
#     +--------------+--------------+------+-----+---------+----------------+
#     | Field        | Type         | Null | Key | Default | Extra          |
#     +--------------+--------------+------+-----+---------+----------------+
#     | subscriberId | int(11)      | NO   | PRI | NULL    | auto_increment |
#     | firstName    | varchar(255) | YES  |     | NULL    |                |
#     | lastName     | varchar(255) | YES  |     | NULL    |                |
#     | email        | varchar(255) | NO   | UNI | NULL    |                |
#     +--------------+--------------+------+-----+---------+----------------+
#     interest:
#     +--------------+--------------+------+-----+---------+----------------+
#     | Field        | Type         | Null | Key | Default | Extra          |
#     +--------------+--------------+------+-----+---------+----------------+
#     | InterestId   | int(11)      | NO   | PRI | NULL    | auto_increment |
#     | subscriberId | int(11)      | NO   | MUL | NULL    |                |
#     | category*    | tinyint(4)   | NO   |     | NULL    |                |
#     | phrase       | varchar(255) | NO   |     | NULL    |                |
#     +--------------+--------------+------+-----+---------+----------------+
#     '*category: 0 - area, 1- general_journal, 2 - expert_journal, 3 - keyword, 4 - author'
#     '''
#     phdb.createTableSubscriber()
#     phdb.createTableInterest()
#     ldSubscriber = [
#                     {'firstName':'Franklin', 'lastName':'Zhong', 'email':'franklin.zhong@gmail.com'}, 
#                     {'firstName':'Zhi', 'lastName':'Li', 'email':'henrylee18@yahoo.com'}, 
#                     ]
#     ldInterest = [
#                     {'subscriberId':'1', 'category':'0', 'phrase':'biochemistry'}, 
#                     {'subscriberId':'1', 'category':'0', 'phrase':'cell biology'}, 
#                     {'subscriberId':'1', 'category':'1', 'phrase':'Nature'}, 
#                     {'subscriberId':'1', 'category':'1', 'phrase':'Science'}, 
#                     {'subscriberId':'1', 'category':'1', 'phrase':'Cell'}, 
#                     {'subscriberId':'1', 'category':'2', 'phrase':'Molecular Cell'}, 
#                     {'subscriberId':'1', 'category':'2', 'phrase':'Nature structural and Molecular Biology'}, 
#                     {'subscriberId':'1', 'category':'2', 'phrase':'Molecular and Cellular Biology'}, 
#                     {'subscriberId':'1', 'category':'3', 'phrase':'telomerase and cancer biology'}, 
#                     {'subscriberId':'1', 'category':'3', 'phrase':'telomere and DNA replication'}, 
#                      
#                     {'subscriberId':'2', 'category':'0', 'phrase':'biochemistry'}, 
#                     {'subscriberId':'2', 'category':'0', 'phrase':'Immunology'}, 
#                     {'subscriberId':'2', 'category':'1', 'phrase':'Nature'}, 
#                     {'subscriberId':'2', 'category':'1', 'phrase':'Science'}, 
#                     {'subscriberId':'2', 'category':'2', 'phrase':'Immunity'}, 
#                     {'subscriberId':'2', 'category':'2', 'phrase':'Journal of Immunology'}, 
#                     {'subscriberId':'2', 'category':'2', 'phrase':'Molecular Cell'}, 
#                     {'subscriberId':'2', 'category':'2', 'phrase':'Nature structural and Molecular Biology'}, 
#                     {'subscriberId':'2', 'category':'3', 'phrase':'noncoding RNA'}, 
#  
#                     ]
#     phdb.insertMany('subscriber', ldSubscriber)
#     phdb.insertMany('interest', ldInterest)
#      
#      
#     'close pubhub database'    
#     phdb.close()
    
    
    
    '''
    =====================================================================
    Already in database:
    =====================================================================
    '''
    '''
    table article
    
    table author
    
    table subscriber:
    +--------------+-----------+----------+--------------------------+
    | subscriberId | firstName | lastName | email                    |
    +--------------+-----------+----------+--------------------------+
    |            1 | Franklin  | Zhong    | franklin.zhong@gmail.com |
    |            2 | Zhi       | Li       | henrylee18@yahoo.com     |
    +--------------+-----------+----------+--------------------------+

    table interest:
    +------------+--------------+----------+-----------------------------------------+
    | InterestId | subscriberId | category | phrase                                  |
    +------------+--------------+----------+-----------------------------------------+
    |          1 |            1 |        0 | biochemistry                            |
    |          2 |            1 |        0 | cell biology                            |
    |          5 |            1 |        1 | Cell                                    |
    |          3 |            1 |        1 | Nature                                  |
    |          4 |            1 |        1 | Science                                 |
    |          8 |            1 |        2 | Molecular and Cellular Biology          |
    |          6 |            1 |        2 | Molecular Cell                          |
    |          7 |            1 |        2 | Nature structural and Molecular Biology |
    |          9 |            1 |        3 | telomerase and cancer biology           |
    |         10 |            1 |        3 | telomere and DNA replication            |
    |         11 |            2 |        0 | biochemistry                            |
    |         12 |            2 |        0 | Immunology                              |
    |         13 |            2 |        1 | Nature                                  |
    |         14 |            2 |        1 | Science                                 |
    |         15 |            2 |        2 | Immunity                                |
    |         16 |            2 |        2 | Journal of Immunology                   |
    |         17 |            2 |        2 | Molecular Cell                          |
    |         18 |            2 |        2 | Nature structural and Molecular Biology |
    |         19 |            2 |        3 | noncoding RNA                           |
    +------------+--------------+----------+-----------------------------------------+    
    '''
    
    '''
    =====================================================================
    At a given time, query Pubmed and store new results since last query
    time in database
    =====================================================================
    '''

    pubmedQueryInterval = 7 * 24 * 3600 # in seconds 
    lastQueryTime = time.time() - pubmedQueryInterval
    
    queryPubmedAndStoreResults(lastQueryTime)
    
    
    
    
    
    
    
# #     queryStr = '"Nature"[Journal]+AND+(2014/04/20[PDAT]+:+2014/04/26[PDAT])+AND+Journal+Article[ptyp]'
# #     queryStr = '("Nature"[Journal])+AND+(2014/04/20[PDAT]+:+2014/04/26[PDAT])'
#     queryStr = '("Nature"[Journal])+AND+(2014/04/21[PDAT]+:+3000/01/01[PDAT])+AND+(Journal+Article[ptyp])'
# #     queryStr = 'Nature[Journal]+AND+(2008/11/01[PDAT]+:+2012/11/12[PDAT])'
# #     queryStr = 'Science[Journal]+AND+(2008/11/01[PDAT]+:+2012/11/12[PDAT])'
# #     queryStr = 'Science[Journal]+AND+(2005/07/01[PDAT]+:+2010/07/12[PDAT])'
# #     queryStr = 'Cell[Journal]+AND+(2008/07/01[PDAT]+:+2010/07/12[PDAT])'
# #     queryStr = 'Nature[Journal]+AND+(2012/07/01[PDAT]+:+2012/07/12[PDAT])'
# #     queryStr = 'Molecular+Cell[Journal]+AND+(2010/05/01[PDAT]+:+2010/07/12[PDAT])'
# #     queryStr = 'Molecular+and+cellular+biology[Journal]+AND+(2010/05/01[PDAT]+:+2011/07/12[PDAT])'
# #     queryStr = '(telomere+and+DNA+replication)+AND+(2010/05/01[PDAT]+:+2011/07/12[PDAT])'
#            
#     'query pubmed'
#     pa = PubmedApi()
#     ldArticle, ldAuthor = pa.query(queryStr, 5)
#    
#     'connect pubhub database'
#     phdb = PhDatabase(MysqlConnection('pubhub', '54.187.112.65', 'root', 'lymanDelmedio123'))    
#     
#     'record article'
#     phdb.insertMany('article', ldArticle)
#    
#     'record author'
#     #Need to look up articleId in article, replace key PMID with articleID
#     replaceKeyValuePair(phdb, ldAuthor, 'article', 'PMID', 'articleId')
#     phdb.insertMany('author', ldAuthor)
#    
#     'close pubhub database'
#     phdb.close()
    
    '================================'
    'doc tests'
    '================================'

    import doctest
    print doctest.testmod()
         
    '================================'
    'done'
    '================================'
    
    logging.info('\n\nDone.\n')

    
    
    
    
    