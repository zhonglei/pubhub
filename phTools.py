'''
Created on Apr 12, 2014

@author: zhil2
'''

import logging

def findAllAndAssert(node,tag,reSymbol):
    '''
    Find in current node\'s children with tag, and assert if the regular
    expression symbol reSymbol is satisfied. Node should be a node in 
    xml.etree.ElementTree constructed from an XML file.
    reSymbol:
    * -- 0 or more
    + -- 1 or more
    ? -- 0 or 1
    {n} -- exactly n
    '''
    l=node.findall(tag)
    ll=len(l)
    wf = False # warning flag
    if reSymbol=='*':
        #assert(ll>=0)
        if ll < 0:
            wf = True
    elif reSymbol=='+':
        #assert(ll>=1)
        if ll < 1:
            wf = True
    elif reSymbol=='?':
        #assert(ll==0 or ll==1)
        if ll != 0 and ll != 1:
            wf = True            
    else:
        #assert(False) #FIXME: add {n} later
        wf = True
    if wf == True:
        logging.warning('unexpected number of nodes: %d.' % ll)            
    return l

class MyException(Exception):
    '''
    Example:
    >>> try:
    ...     raise MyException("test exception")
    ... except MyException as e:
    ...     print e
    MyException: test exception
    
    '''
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        myStr="MyException: "+str(self.msg)
        return myStr
         
def myNormalizedDate(dateString):
    '''
    Example:
    >>> myNormalizedDate('2010-Aug-26')
    '2010-8-26'
    >>> myNormalizedDate('')
    ''
    >>> myNormalizedDate('2010-10,26')
    '2010-10,26'
    >>> myNormalizedDate('2010-10-26')
    '2010-10-26'
    >>> myNormalizedDate('2010-Jun')
    '2010-6'
    >>> myNormalizedDate('2010')
    '2010'
    >>> myNormalizedDate('2014-Apr-16')
    '2014-4-16'
    '''        
    return dateString.replace('Jan','1').replace('Feb','2') \
           .replace('Mar','3').replace('Apr','4').replace('May','5') \
           .replace('Jun','6').replace('Jul','7').replace('Aug','8') \
           .replace('Sep','9').replace('Oct','10').replace('Nov','11') \
           .replace('Dec','12')
           
def singleStrip(t):
    '''
    Example:
    >>> singleStrip(((1L,), (2L,)))
    [1L, 2L]
    '''
    return[(lambda y: y[0])(x) for x in t]           
                    
if __name__ == '__main__':
    import doctest
    print doctest.testmod()
    
    
