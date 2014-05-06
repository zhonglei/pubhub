'''

Methods for updating Pubhub database.

Created on May 2, 2014

@author: zhil2
'''

import time
from phController import queryPubmedAndStoreResults
from phDatabaseApi import PhDatabase, MysqlConnection
from phInfo import phDbInfo
import logging
from logging import info
import sys

'''
format '%(asctime)s %(name)s %(levelname)s: %(message)s'
level DEBUG, INFO
'''
# logging.basicConfig(format='%(name)s %(levelname)s: %(message)s',
#                     level=logging.DEBUG)

if __name__ == '__main__':
    
    import doctest
    print doctest.testmod()
    
    'if with argument --doctest-only, skip the rest'
    'if with argument --format, also call formatDatabase'
    formatFlag = False
    if len(sys.argv) > 1:
        for a in sys.argv[1:]:
            if a == '--doctest-only':
                sys.exit()
            elif a == '--format-database':
                print 'Format database: all data will be lost! Sure? (Yes/No)'
                line = sys.stdin.readline()
                if line == 'Yes\n':
                    print 'Are you absolutely sure you want to proceed? (Yes/No)'
                    line = sys.stdin.readline()
                    if line == 'Yes\n':
                        formatFlag = True
                        continue                
                sys.exit()

    '================================'
    'format Pubhub database'
    '================================'
    if formatFlag:
        print 'proceed to format database...'
        phdb = PhDatabase(MysqlConnection(phDbInfo['dbName'],phDbInfo['ip'],
                                    phDbInfo['user'],phDbInfo['password']))
        phdb.formatDatabase()
        phdb.close()
            
    '================================'
    'query Pubmed and store results'
    '================================'

    print 'query Pubmed and store results...'
    pubmedQueryInterval = 28 * 24 * 3600 # 7 days in seconds 
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
#     phdb = PhDatabase(MysqlConnection(phDbInfo['dbName'],phDbInfo['ip'],
#                                      phDbInfo['user'],phDbInfo['password']))    
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

    print '\nDone.'
