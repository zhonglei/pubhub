'''
Formatting Pubhub database.

Created on May 2, 2014

@author: zhil2
'''

import sys
import time

from phInfo import phDbInfo, pubmedBacktrackSecondForNewSubscriber
from phDatabaseApi import PhDatabase, MysqlConnection
from phController import signUpSubscriber, queryPubmedAndStoreResults

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
    'if with argument --format-database, also call _formatDatabase'
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
        
        phdb._formatDatabase()

        now = time.time()
        queryStartTime = now - pubmedBacktrackSecondForNewSubscriber
        queryEndTime = now

        phdb.close()

        'Preload subscribers and query Pubmed'
        subscriberId = signUpSubscriber(phDbInfo, 'zhonglei@stanford.edu', '123', '', 'Artandi Lab', '5', 
                         ['telomerase','telomere'])
        queryPubmedAndStoreResults(phDbInfo, queryStartTime, queryEndTime, subscriberId)
        
        subscriberId = signUpSubscriber(phDbInfo, 'leeoz@stanford.edu', '123', '', 'Chang Lab', '5', 
                         ['noncoding RNA','lncRNA','chromatin'])
        queryPubmedAndStoreResults(phDbInfo, queryStartTime, queryEndTime, subscriberId)
        
        subscriberId = signUpSubscriber(phDbInfo, 'lizhi1981@gmail.com', '123', 'Zhi', 'Li', '1', 
                         ['DNA sequencing'])
        queryPubmedAndStoreResults(phDbInfo, queryStartTime, queryEndTime, subscriberId)

        
    else:
        print '\nDid not execute formatting database.'             
            
    print '\nDone.'
