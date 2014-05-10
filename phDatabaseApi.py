'''

Classes and methods for accessing the Pubhub database.

Created on Apr 25, 2014

@author: zhil2
'''

import MySQLdb
from logging import warning, debug
import pprint
import time
import datetime

from phInfo import BiologyResearchInfo
# from phInfo import TestSubscriberInfo
from phTools import replaceKeyValuePair

'''
format '%(asctime)s %(name)s %(levelname)s: %(message)s'
level DEBUG, INFO
'''
# import logging
# logging.basicConfig(format='%(name)s %(levelname)s: %(message)s',
#                     level=logging.DEBUG)

class DbConnection(object):
    
    def __init__(self, n, h='localhost', u='root', p=''):
        self.dbName = n
        self.host = h
        self.user = u
        self.password = p
        self.conn = None
        
    def _close(self):
        '''
        Return value: -1 if connection does not exist; 0 otherwise.
        '''
        if self.conn:
            self.conn.close()
            return 0
        return -1
                                             
class MysqlConnection(DbConnection):

    '''
    Example:
    >>> from phInfo import testDbInfo
    >>> conn = MysqlConnection(testDbInfo['dbName'],testDbInfo['ip'],testDbInfo['user'],testDbInfo['password'])
    >>> conn._execute('Drop table Dict')
    0
    >>> conn._execute('CREATE TABLE Dict (k VARCHAR(255), v VARCHAR(255));')
    0
    >>> conn._execute('INSERT INTO Dict (k, v) VALUES (%s,%s)', ("Zhi","32"))
    0
    >>> conn._execute('INSERT INTO Dict (k, v) VALUES (%s,%s)', ("Hu","28"))
    0
    >>> conn._execute('INSERT INTO Dict (k, v) VALUES (%s,%s)', ("Russ","31"))
    0
    >>> conn._commit()
    0
    >>> _,ret = conn._fetchall('SELECT DISTINCT k FROM Dict')
    >>> print ret
    ((u'Zhi',), (u'Hu',), (u'Russ',))
    >>> conn._close()
    0
    '''

    def __init__(self, n, h, u, p):
        super(MysqlConnection,self).__init__(n,h,u,p)
        try:
            self.conn = MySQLdb.connect(self.host,self.user,self.password,
                            self.dbName,use_unicode=True, charset='utf8')
        except MySQLdb.Error as e:
            warning(e)
        except Exception as e:
            warning(e)        
    
    def _execute(self,query,fields=None):
        '''
        Return value: -1 if connection does not exist; 0 if execution succeeds;
        1 if MySQLdb error; 2 if other errors.
        '''
        if self.conn:
            try:            
                cursor=self.conn.cursor()
                if fields is None:
                    cursor.execute(query)
                else:
                    cursor.execute(query,fields)
            except MySQLdb.IntegrityError as e:
                warning(e)
                raise e
            except MySQLdb.Error as e:
                warning(e)
                return 1
            except Exception as e:
                warning(e)
                return 2
            else:
                return 0
        return -1

    def _fetchall(self,query,fields=None):
        '''
        Return values: First argument: -1 if connection does not exist; 0 if 
        execution succeeds; 1 if MySQLdb error; 2 if other errors. Second
        argument: fetched values in tuples if execution succeeds; None otherwise.
        '''        
        if self.conn:
            try:            
                cursor=self.conn.cursor()
                if fields is None:
                    cursor.execute(query)
                else:
                    cursor.execute(query,fields)
            except MySQLdb.Error as e:
                warning(e)
                return (1, None)
            except Exception as e:
                warning(e)
                return (2, None)
            else:
                res = cursor.fetchall()
                return (0, res)
        return (-1, None)
        
    def _commit(self):
        '''
        Return value: -1 if connection does not exist; 0 if commit succeeds;
        1 if MySQLdb error; 2 if other errors.
        '''
        if self.conn:
            try:
                self.conn.commit()
            except MySQLdb.Error as e:
                debug("database commit failed. roll back.")
                self.conn.rollback()
                warning(e)
                return 1
            except Exception as e:
                warning(e)
                return 2
            else:
                debug("database commit successful.")
                return 0
        return -1

class Database(object):

    def __init__(self,conn):
        self.conn = conn
        
    def close(self):
        self.conn._close()
                
class PhDatabase(Database):

    def _formatDatabase(self):
        '''
        Format database by cleaning data. Use with caution!!
        
        Example:
        >>> from phInfo import testDbInfo
        >>> phdb = PhDatabase(MysqlConnection(testDbInfo['dbName'],testDbInfo['ip'],testDbInfo['user'],testDbInfo['password']))
        >>> phdb._formatDatabase()
        >>> phdb.close()
        '''
        if self.conn:
            pass
            
            self.conn._execute('DROP TABLE subscriber_articleEvent')
            self.conn._execute('DROP TABLE subscriber_article')
            self.conn._execute('DROP VIEW firstAuthor')
            self.conn._execute('DROP VIEW lastAuthor')
            self.conn._execute('DROP TABLE author')
            self.conn._execute('DROP TABLE article')
            self.conn._execute('DROP TABLE interest')
            self.conn._execute('DROP TABLE subscriber')
            self.conn._execute('DROP TABLE journal_area')
            self.conn._execute('DROP TABLE journal')
            self.conn._execute('DROP TABLE area')
            self.conn._execute('DROP TABLE phDatabaseUpdateEvent')
             
            self.createTablePhDatabaseUpdateEvent()

            self.createTableArea()
            self.preloadTableArea()
 
            self.createTableJournal()
            self.preloadTableJournal()

            self.createTableJournal_Area()
            self.preloadTableJournal_Area()
 
            self.createTableSubscriber()
            self.createTableInterest()
            #self.preloadTableSubscriberAndInterestWithSample()
                 
            self.createTableArticle()
             
            self.createTableAuthor()
            self.createViewLastAuthor()
            self.createViewFirstAuthor()
             
            self.createTableSubscriber_Article()
            self.createTableSubscriber_ArticleEvent()

    '===================================================='
    '==============create table begins==================='
    '===================================================='
            
    def createTablePhDatabaseUpdateEvent(self):
        query='''CREATE TABLE phDatabaseUpdateEvent(
                updateEventId INT NOT NULL AUTO_INCREMENT,
                timestamp DATETIME NOT NULL,
                PRIMARY KEY (updateEventId)
                );
        '''
        debug('query:\n'+query)
        if self.conn:
            return self.conn._execute(query)
        return -1

    def createTableArea(self):
        query='''CREATE TABLE area(
            areaId TINYINT NOT NULL,
            areaName VARCHAR(255) NOT NULL,
            PRIMARY KEY (areaId),
            CONSTRAINT uc_areaName UNIQUE (areaName)
            );
        '''
        debug('query:\n'+query)
        if self.conn:
            return self.conn._execute(query)
        return -1
        
    def preloadTableArea(self):
        preload=[]
        listArea = BiologyResearchInfo.getListArea()
        for areaId, areaName in listArea:
            preload.append({'areaId':areaId,'areaName':areaName})
        return self.insertMany('area',preload)

    def createTableJournal(self):
        query='''CREATE TABLE journal(
            journalId INT NOT NULL AUTO_INCREMENT,
            journalTitle VARCHAR(255) NOT NULL,
            journalBriefTitle VARCHAR(255),
            isGeneral BOOLEAN NOT NULL,
            PRIMARY KEY (journalId),
            CONSTRAINT uc_journalTitle UNIQUE (journalTitle)
            );
        '''
        debug('query:\n'+query)
        if self.conn:
            return self.conn._execute(query)
        return -1

    def preloadTableJournal(self):
        preload=[]
        dictJournal_Area = BiologyResearchInfo.getDictJournal_Area()
        listGeneralJournal = BiologyResearchInfo.getListGeneralJournal()
        for journalTitle in dictJournal_Area.keys():
            d = {}
            d['journalTitle'] = journalTitle
            if journalTitle in listGeneralJournal:
                d['isGeneral'] = 1 #True for BOOLEAN type
            else:
                d['isGeneral'] = 0 #False for BOOLEAN type
            preload.append(d)
        
        return self.insertMany('journal',preload)

    def createTableJournal_Area(self):
        query='''CREATE TABLE journal_area(
                journal_areaId INT NOT NULL AUTO_INCREMENT,
                journalId INT NOT NULL,
                areaId TINYINT NOT NULL,
                PRIMARY KEY (journal_areaId),
                FOREIGN KEY (journalId) REFERENCES journal(journalId),
                FOREIGN KEY (areaId) REFERENCES area(areaId),
                CONSTRAINT uc_journal_area UNIQUE (journalId,areaId)
                );
        '''
        debug('query:\n'+query)
        if self.conn:
            return self.conn._execute(query)
        return -1
    
    def preloadTableJournal_Area(self):
        preload=[]
        dictJournal_Area = BiologyResearchInfo.getDictJournal_Area()
        for journalTitle in dictJournal_Area.keys():
            listAreaId = dictJournal_Area[journalTitle]
            for areaId in listAreaId:
                preload.append({'journalTitle':journalTitle, 'areaId':areaId})
        replaceKeyValuePair(self,preload,'journal','journalTitle','journalId')
        
        return self.insertMany('journal_area',preload)

    def createTableSubscriber(self):
        query='''CREATE TABLE subscriber(
            subscriberId INT NOT NULL AUTO_INCREMENT,
            firstName VARCHAR(255),
            lastName VARCHAR(255),
            email VARCHAR(255) NOT NULL,
            password VARCHAR(255),
            PRIMARY KEY (subscriberId),
            CONSTRAINT uc_email UNIQUE (email)
            );
        '''
        debug('query:\n'+query)
        if self.conn:
            return self.conn._execute(query)
        return -1

    def createTableInterest(self):
        query='''CREATE TABLE interest(
                InterestId INT NOT NULL AUTO_INCREMENT,
                subscriberId INT NOT NULL,
                category TINYINT NOT NULL COMMENT 'category: 1 - area, 2- generalJournal, 3 - expertJournal, 4 - keyword, 5 - author, ...',
                phrase VARCHAR(255) NOT NULL,
                PRIMARY KEY (interestId),
                FOREIGN KEY (subscriberId) REFERENCES subscriber(subscriberId),
                CONSTRAINT uc_subscriber_category_phrase UNIQUE (subscriberId, category, phrase)
                );
        '''
        debug('query:\n'+query)
        if self.conn:
            return self.conn._execute(query)
        return -1 

#     def preloadTableSubscriberAndInterestWithSample(self):
#         
#         ldSubscriber = TestSubscriberInfo.getLdSubscriber()
#         ldInterest = TestSubscriberInfo.getLdInterest()
#         self.insertMany('subscriber', ldSubscriber)        
#         replaceKeyValuePair(self,ldInterest,'subscriber','email','subscriberId')
#         self.insertMany('interest', ldInterest)

    def createTableArticle(self):
        query='''CREATE TABLE article(
                articleId INT NOT NULL AUTO_INCREMENT, 
                PMID INT,
                DateCreated DATE,
                JournalVolume MEDIUMINT,
                JournalIssue MEDIUMINT,
                PubDate DATE,
                JournalTitle VARCHAR(255),
                JournalISOAbbreviation VARCHAR(255),
                ArticleTitle VARCHAR(255),
                DoiId VARCHAR(255),
                Abstract TEXT,
                PRIMARY KEY (articleId),
                CONSTRAINT uc_PMID UNIQUE (PMID)
                );
        '''
        debug('query:\n'+query)
        if self.conn:
            return self.conn._execute(query)
        return -1

    ''' must create index on article.DateCreated:
    CREATE INDEX idx_DateCreated ON article (DateCreated)
    '''

    def createTableAuthor(self):
        query='''CREATE TABLE author(
                authorId INT NOT NULL AUTO_INCREMENT,
                articleId INT NOT NULL,
                ForeName VARCHAR(255),
                Initials VARCHAR(255),
                LastName VARCHAR(255),
                Affiliation TEXT,
                AuthorOrder SMALLINT NOT NULL,
                AuthorOrderReversed SMALLINT NOT NULL,
                PRIMARY KEY (authorId),
                FOREIGN KEY (articleId) REFERENCES article(articleId),
                CONSTRAINT uc_article_order UNIQUE (articleId, AuthorOrder)
                );
        '''
        debug('query:\n'+query)
        if self.conn:
            return self.conn._execute(query)
        return -1
    
    ''' must create index on author.authorId:
    CREATE INDEX idx_articleId ON author (articleId)
    '''

    def createViewFirstAuthor(self):
        query='''CREATE VIEW firstAuthor AS 
                    SELECT * FROM author 
                    WHERE AuthorOrder = 1;
        '''
        debug('query:\n'+query)
        if self.conn:
            return self.conn._execute(query)
        return -1

    def createViewLastAuthor(self):
        query='''CREATE VIEW lastAuthor AS 
                    SELECT * FROM author 
                    WHERE AuthorOrderReversed = 1;
        '''
        debug('query:\n'+query)
        if self.conn:
            return self.conn._execute(query)
        return -1    
        
    def createTableSubscriber_Article(self):
        query='''CREATE TABLE subscriber_article(
                subscriber_articleId INT NOT NULL AUTO_INCREMENT,
                subscriberId INT NOT NULL,
                articleId INT NOT NULL,
                queryPhrase VARCHAR(255),
                PRIMARY KEY (subscriber_articleId),
                FOREIGN KEY (subscriberId) REFERENCES subscriber(subscriberId),
                FOREIGN KEY (articleId) REFERENCES article(articleId),
                CONSTRAINT uc_subscriber_article_queryphrase UNIQUE (subscriberId,articleId,queryPhrase)
                );
        '''
        debug('query:\n'+query)
        if self.conn:
            return self.conn._execute(query)
        return -1

    ''' must create index on subscriber_article.articleId:
    CREATE INDEX idx_articleId ON subscriber_article (articleId)
    '''
    ''' must create index on subscriber_article.subscriberId:
    CREATE INDEX idx_subscriberId ON subscriber_article (subscriberId)
    '''
    
    def createTableSubscriber_ArticleEvent(self):
        query='''CREATE TABLE subscriber_articleEvent(
                subscriber_articleEventId INT NOT NULL AUTO_INCREMENT,
                subscriber_articleId INT NOT NULL,
                timestamp DATETIME NOT NULL,
                category TINYINT NOT NULL COMMENT 'category: 1 - created, 2 - pinned, 3 - moreClicked, 4 - extlinkClicked, ...',
                status BOOLEAN NOT NULL,
                extraInfo TEXT,
                PRIMARY KEY (subscriber_articleEventId),
                FOREIGN KEY (subscriber_articleId) REFERENCES subscriber_article(subscriber_articleId)
                );
        '''
        debug('query:\n'+query)
        if self.conn:
            return self.conn._execute(query)
        return -1
        
    '===================================================='
    '================create table ends==================='
    '===================================================='
            
    def insertOneReturnLastInsertId(self,tableName,d):
        '''
        Insert one record and return the last insert id (MySQL LAST_INSERT_ID()
        method). Return: -1 if the operation fails, the ID otherwise.
        The input dict must contains a key corresponding to a field with
        AUTO_INCREMENT property in the table tableName.
        
        Returned value: 
        
        Example:
        >>> from phInfo import testDbInfo
        >>> phdb = PhDatabase(MysqlConnection(testDbInfo['dbName'],testDbInfo['ip'],testDbInfo['user'],testDbInfo['password']))
        >>> phdb._formatDatabase()
        >>> dSubscriber1 = {'subscriberId':None,'firstName':'Russ', 'lastName':'Li', 'email':'iamjingxian@gmail.com'}
        >>> phdb.insertOneReturnLastInsertId('subscriber',dSubscriber1)
        1L
        >>> dSubscriber2 = {'subscriberId':None,'firstName':'Hu', 'lastName':'Wang', 'email':'wanghugigi@gmail.com'}
        >>> phdb.insertOneReturnLastInsertId('subscriber',dSubscriber2)
        2L
        >>> phdb.close()
        '''
        ret = self.insertOne(tableName,d)
        if ret != 0:
            return -1
        ret, res = self.conn._fetchall("SELECT LAST_INSERT_ID()")
        if ret !=0:
            return -1
        return res[0][0]
    
    def insertOne(self,tableName,d):
        nSuccessful = 0
        
        query = 'INSERT INTO ' + tableName + ' ('
        for k in d.keys()[:-1]:
            query += k + ', '
        query += d.keys()[-1]
        query += ') VALUES ('
        for k in d.keys()[:-1]:
            query += '%s' + ', '
        query += '%s'
        query += ')'
        
        fields = tuple(d.values())

        debug('query:\n'+query)
        debug('fields:\n'+str(fields))
        
        if self.conn:
            ret = self.conn._execute(query,fields)
            if ret == 0:
                nSuccessful += 1

        r = self.conn._commit()
        if r == 0:
            if nSuccessful == 1:
                debug('%d of %d records inserted into %s successfully.' \
                              % (nSuccessful, 1, tableName))
                return 0
            else: 
                warning('%d of %d inserted into %s successfully.' \
                              % (nSuccessful, 1, tableName))
                return 1
        else:
            warning('insertOne commit failed.')
            return 2
    
    
    def insertMany(self,tableName,listDict):
        '''
        Return value: 0 if all insertions succeed; 1 if commit succeeds but not
        all insertion succeeds; 2 if commit fails.
        
        Examples:
        >>> from phInfo import testDbInfo
        >>> phdb = PhDatabase(MysqlConnection(testDbInfo['dbName'],testDbInfo['ip'],testDbInfo['user'],testDbInfo['password']))
        >>> phdb.conn._execute('Drop table Dict')
        0
        >>> phdb.conn._execute('CREATE TABLE Dict (k VARCHAR(255), v VARCHAR(255));')
        0
        >>> phdb.conn._execute('INSERT INTO Dict (k, v) VALUES (%s,%s)', ("Zhi","32"))
        0
        >>> phdb.conn._execute('INSERT INTO Dict (k, v) VALUES (%s,%s)', ("Hu","28"))
        0
        >>> phdb.conn._execute('INSERT INTO Dict (k, v) VALUES (%s,%s)', ("Russ","31"))
        0
        >>> phdb.conn._commit()
        0
        >>> phdb.insertMany('Dict',[{'k':'Lala','v':'31'},{'k':'Franklin','v':'31'},{'k':'Yang','v':'31'}])
        0
        >>> _, res = phdb.selectDistinct('Dict',['k','v'])
        >>> print res
        ((u'Zhi', u'32'), (u'Hu', u'28'), (u'Russ', u'31'), (u'Lala', u'31'), (u'Franklin', u'31'), (u'Yang', u'31'))
        >>> phdb.close()
        '''
    
        nSuccessful = 0
        for d in listDict:
            query = 'INSERT INTO ' + tableName + ' ('
            for k in d.keys()[:-1]:
                query += k + ', '
            query += d.keys()[-1]
            query += ') VALUES ('
            for k in d.keys()[:-1]:
                query += '%s' + ', '
            query += '%s'
            query += ')'
            
            fields = tuple(d.values())

            debug('query:\n'+query)
            debug('fields:\n'+str(fields))
            
            if self.conn:
                try:
                    ret = self.conn._execute(query,fields)
                except MySQLdb.IntegrityError:
                    '''For insertMany, raised IntegrityError should not stop 
                    program from continue running the rest of insertions'''
                    pass 
                else:
                    if ret == 0:
                        nSuccessful += 1

        r = self.conn._commit()
        if r == 0:
            if nSuccessful == len(listDict):
                #debug('%d of %d records inserted into %s successfully.' \
                #              % (nSuccessful, len(listDict), tableName))
                return 0
            else: 
                warning('%d of %d inserted into %s successfully.' \
                              % (nSuccessful, len(listDict), tableName))
                return 1
        else:
            warning('insertMany commit failed.')
            return 2
    
    def selectDistinct(self,tableName,listColumn,condition=None):
        '''
        flag, res = phdb.selectDistinct('Dict',['k','v'])
        SELECT DISTINCT k, v FROM Dict
        '''
        query = 'SELECT DISTINCT '
        for c in listColumn[:-1]:
            query += c + ', '
        query += listColumn[-1] + ' '
        query += 'FROM '+tableName
         
        if condition:
            query += ' WHERE '+condition
                
        debug('query:\n'+query)
        
        ret, res = self.conn._fetchall(query)
        
        debug('fetched result:\n'+ pprint.pformat(res))
        
        return (ret, res)
    
    def fetchall(self,query,fields=None):
        debug('query:\n'+query)
        ret, res = self.conn._fetchall(query,fields=None)
        debug('fetched result:\n'+ pprint.pformat(res))        
        return (ret, res)
        
def constructMysqlDatetimeStr(t):
    '''
    Example:
    >>> constructMysqlDatetimeStr(1398036175.4)
    '2014-04-20 23:22:55'
    '''
    
    return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(t))
    #return datetime.datetime.utcfromtimestamp(t)
        
                        
if __name__ == '__main__':
    import doctest
    print doctest.testmod()
