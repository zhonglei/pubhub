'''

Methods for sending email to subscribers.

Created on May 3, 2014

@author: zhil2
'''

import sys

from phInfo import phDbInfo, emailInfo
from phController import emailListArticleToSubscriber
    
if __name__ == '__main__':
    
#     import doctest
#     print doctest.testmod()
    
    'if with argument --doctest-only, skip the rest'
    if len(sys.argv) > 1:
        for a in sys.argv[1:]: 
            if a =='--doctest-only':
                sys.exit()
    
    subscriberId = 3
    sinceDaysAgo = 7
    emailListArticleToSubscriber(phDbInfo, emailInfo, subscriberId, sinceDaysAgo) 
    
    print 'Done.'
    