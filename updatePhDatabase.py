'''

Updating Pubhub database.

Created on May 2, 2014

@author: zhil2
'''

import time
import sys

from phInfo import phDbInfo, pubmedBacktrackSecondForNewSubscriber
from phController import queryPubmedAndStoreResults, getLastPhDatabaseUpdateTime

'''
format '%(asctime)s %(name)s %(levelname)s: %(message)s'
level DEBUG, INFO
'''
# import logging
# logging.basicConfig(format='%(name)s %(levelname)s: %(message)s',
#                     level=logging.DEBUG)

if __name__ == '__main__':
    
    import doctest
    print doctest.testmod()

    'if with argument --doctest-only, skip the rest'
    if len(sys.argv) > 1:
        for a in sys.argv[1:]: 
            if a =='--doctest-only':
                sys.exit()
                
    '================================'
    'query Pubmed and store results'
    '================================'

    print 'query Pubmed and store results...'

    now = time.time()
    
    queryStartTime = getLastPhDatabaseUpdateTime(phDbInfo)
    
    'In the rarest case there is no records for last PhDatabase update'
    if queryStartTime is None: # No records, first time
        queryStartTime = now - pubmedBacktrackSecondForNewSubscriber

    queryEndTime = now
    
    queryPubmedAndStoreResults(phDbInfo, queryStartTime, queryEndTime)

    print '\nDone.'
