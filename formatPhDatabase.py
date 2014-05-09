'''
Formatting Pubhub database.

Created on May 2, 2014

@author: zhil2
'''

import sys
import time

from phInfo import phDbInfo
from phDatabaseApi import PhDatabase, MysqlConnection
from phController import signUpSubscriber, queryPubmedAndStoreResults
from phInfo import pubmedBacktrackSecondForNewSubscriber

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

        'Preload subscribers and query Pubmed'
        subscriberId = signUpSubscriber('zhonglei@stanford.edu', '', 'ArtandiLab', '5', 
                         ['telomerase','telomere'])
        queryPubmedAndStoreResults(queryStartTime, queryEndTime, subscriberId)
        
        subscriberId = signUpSubscriber('leeoz@stanford.edu', '', 'ChangLab', '5', 
                         ['noncoding RNA','lncRNA','chromatin'])
        queryPubmedAndStoreResults(queryStartTime, queryEndTime, subscriberId)
        
        subscriberId = signUpSubscriber('lizhi1981@gmail.com', 'Zhi', 'Li', '1', 
                         ['DNA sequencing'])
        queryPubmedAndStoreResults(queryStartTime, queryEndTime, subscriberId)

        
        phdb.close()
    else:
        print '\nDid not execute formatting database.'             
            
    print '\nDone.'
