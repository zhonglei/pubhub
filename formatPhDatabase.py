'''
Formatting Pubhub database.

Created on May 2, 2014

@author: zhil2
'''

import sys

from phInfo import phDbInfo
from phDatabaseApi import PhDatabase, MysqlConnection
from phController import signUpSubscriber

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
    'if with argument --format-database, also call formatDatabase'
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

        'Preload two subscribers: Artandi and Change lab'
        signUpSubscriber('zhonglei@stanford.edu', '', 'ArtandiLab', '5', 
                         ['telomerase','telomere'])
        signUpSubscriber('leeoz@stanford.edu', '', 'ChangLab', '5', 
                         ['noncoding RNA','lncRNA','chromatin'])
        
        phdb.close()
    else:
        print '\nDid not execute formatting database.'             
            
    print '\nDone.'
