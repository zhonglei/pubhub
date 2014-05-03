'''

Update Pubhub database by read subscriber information and accordingly retrieve
from Pubmed.

Created on May 2, 2014

@author: zhil2
'''

import time
from phController import queryPubmedAndStoreResults
from databaseApi import PhDatabase, MysqlConnection

if __name__ == '__main__':

    '================================'
    'clear up data'
    '================================'
    #delete from subscriber_articleEvent;delete from subscriber_article;delete from author;delete from article;
    #delete from interest; delete from subscriber;
    
    '================================'
    'add subscribers and interests'
    '================================'

    if False:
        phdb = PhDatabase(MysqlConnection('pubhub', '54.187.112.65', 'root', 'lymanDelmedio123'))    
        phdb.createTableSubscriber()
        phdb.createTableInterest()
        ldSubscriber = [
                        {'firstName':'Franklin', 'lastName':'Zhong', 'email':'franklin.zhong@gmail.com'}, 
                        {'firstName':'Zhi', 'lastName':'Li', 'email':'henrylee18@yahoo.com'}, 
                        ]
        ldInterest = [
                        {'subscriberId':'7', 'category':'1', 'phrase':'biochemistry'}, 
                        {'subscriberId':'7', 'category':'1', 'phrase':'cell biology'}, 
                        {'subscriberId':'7', 'category':'2', 'phrase':'Nature'}, 
                        {'subscriberId':'7', 'category':'2', 'phrase':'Science'}, 
                        {'subscriberId':'7', 'category':'2', 'phrase':'Cell'}, 
                        {'subscriberId':'7', 'category':'3', 'phrase':'Molecular Cell'}, 
                        {'subscriberId':'7', 'category':'3', 'phrase':'Nature structural and Molecular Biology'}, 
                        {'subscriberId':'7', 'category':'3', 'phrase':'Molecular and Cellular Biology'}, 
                        {'subscriberId':'7', 'category':'4', 'phrase':'telomerase and cancer biology'}, 
                        {'subscriberId':'7', 'category':'4', 'phrase':'telomere and DNA replication'}, 
                          
                        {'subscriberId':'8', 'category':'1', 'phrase':'biochemistry'}, 
                        {'subscriberId':'8', 'category':'1', 'phrase':'Immunology'}, 
                        {'subscriberId':'8', 'category':'2', 'phrase':'Cell'}, 
                        {'subscriberId':'8', 'category':'2', 'phrase':'Science'}, 
                        {'subscriberId':'8', 'category':'3', 'phrase':'Immunity'}, 
                        {'subscriberId':'8', 'category':'3', 'phrase':'Journal of Immunology'}, 
                        {'subscriberId':'8', 'category':'3', 'phrase':'Molecular Cell'}, 
                        {'subscriberId':'8', 'category':'3', 'phrase':'Nature structural and Molecular Biology'}, 
                        {'subscriberId':'8', 'category':'4', 'phrase':'noncoding RNA'}, 
      
                        ]
        phdb.insertMany('subscriber', ldSubscriber)
        phdb.insertMany('interest', ldInterest)
          
        'close pubhub database'    
        phdb.close()
    
    '================================'
    'Query Pubmed and store results'
    '================================'

    if True:
        pubmedQueryInterval = 7 * 24 * 3600 # 7 days in seconds 
        lastQueryTime = time.time() - pubmedQueryInterval
        
        queryPubmedAndStoreResults(lastQueryTime)
    
    '================================'
    'Query Pubmed and store results'
    '================================'
        
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
