'''
Miscellaneous customized tools.

Created on Apr 12, 2014

@author: zhil2
'''

from logging import warning, debug

'''
format '%(asctime)s %(name)s %(levelname)s: %(message)s'
level DEBUG, INFO
'''
# import logging
# logging.basicConfig(format='%(name)s %(levelname)s: %(message)s',
#                     level=logging.DEBUG)

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
        warning('unexpected number of nodes: %d.' % ll)            
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
    #FIXME: add robustness
    return [(lambda y: y[0])(x) for x in t]           

def replaceKeyValuePair(db, listDict, tableName, keyOld, keyNew):
    '''
    Replace a old key-value pair (with key keyOld) in a list of dictionaries 
    (listDict) with a new pair (with key keyNew), based on the old/new key 
    lookup in a database table (tableName). Commonly used because there are 
    many cases one needs to lookup and replace the id column of a table 
    based on another column (for example, look up and replace PMID with 
    articleId in table article).

    Example:
    >>> from phInfo import doctestDbInfo
    >>> from phDatabaseApi import PhDatabase, MysqlConnection
    >>> phdb = PhDatabase(MysqlConnection(doctestDbInfo['dbName'],doctestDbInfo['ip'],doctestDbInfo['user'],doctestDbInfo['password']))
    >>> phdb.conn._execute('DELETE FROM Dict')
    0
    >>> phdb.insertMany('Dict',[{'k':'Zhi','v':'32'},{'k':'Hu','v':'28'},{'k':'Russ','v':'31'},{'k':'Lala','v':'31'},{'k':'Franklin','v':'31'},{'k':'Yang','v':'31'}])
    0
    >>> _,res = phdb.selectDistinct('Dict',['k','v'])
    >>> print res
    ((u'Zhi', u'32'), (u'Hu', u'28'), (u'Russ', u'31'), (u'Lala', u'31'), (u'Franklin', u'31'), (u'Yang', u'31'))
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
            warning(e)
            rf = 1                
        debug(d)
        
    return rf

def getSubscriberDisplayedName(firstName, lastName, email):
    '''
    Examples:
    >>> getSubscriberDisplayedName('Zhi','Li','zhili@gmail.com')
    'Zhi'
    >>> getSubscriberDisplayedName('','','zhili@gmail.com')
    'zhili@gmail.com'
    >>> getSubscriberDisplayedName('','Li','zhili@gmail.com')
    'Li'
    '''
    name = ''
    if firstName:
        name = firstName
    elif lastName:
        name = lastName
    elif email:
        name = email
    else:
        name = 'Stranger'

    return name
                    
if __name__ == '__main__':
    import doctest
    print doctest.testmod()
    
    
