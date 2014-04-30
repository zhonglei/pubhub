'''

API for database.

Created on Apr 25, 2014

@author: zhil2
'''

import MySQLdb
import logging
import pprint

logging.basicConfig(format='%(name)s %(levelname)s: %(message)s',
                    level=logging.INFO)

class DbConnection(object):
    
    def __init__(self, n, h='localhost', u='root', p=''):
        self.dbName = n
        self.host = h
        self.user = u
        self.password = p
        self.conn = None
        
    def _close(self):
        if self.conn:
            self.conn.close()
            return 0
        return -1
                                             
class MysqlConnection(DbConnection):

    '''
    Example:
    >>> conn = MysqlConnection('testdb','54.187.112.65','root','lymanDelmedio123')
    >>> conn._execute('DELETE FROM Dict')
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
    (('Zhi',), ('Hu',), ('Russ',))
    >>> conn._close()
    0
    '''
#     >>> conn._execute('CREATE TABLE Dict (k VARCHAR(255), v VARCHAR(255));')
#     0

    def __init__(self, n, h, u, p):
        super(MysqlConnection,self).__init__(n,h,u,p)
        try:
            self.conn = MySQLdb.connect(self.host,self.user,self.password,self.dbName)
        except MySQLdb.Error as e:
            logging.warning(e)
        except Exception as e:
            logging.warning(e)        
    
    def _execute(self,query,fields=None):
        if self.conn:
            try:            
                cursor=self.conn.cursor()
                if fields is None:
                    cursor.execute(query)
                else:
                    cursor.execute(query,fields)
            except MySQLdb.Error as e:
                logging.warning(e)
                return 1
            except Exception as e:
                logging.warning(e)
                return 2
            else:
                return 0
        return -1

    def _fetchall(self,query,fields=None):
        if self.conn:
            try:            
                cursor=self.conn.cursor()
                if fields is None:
                    cursor.execute(query)
                else:
                    cursor.execute(query,fields)
            except MySQLdb.Error as e:
                logging.warning(e)
                return (1, None)
            except Exception as e:
                logging.warning(e)
                return (2, None)
            else:
                res = cursor.fetchall()
                return (0, res)
        return (-1, None)
        
    def _commit(self):
        if self.conn:
            try:
                self.conn.commit()
            except MySQLdb.Error as e:
                logging.debug("database commit failed. roll back.")
                self.conn.rollback()
                logging.warning(e)
                return 1
            except Exception as e:
                logging.warning(e)
                return 2
            else:
                logging.debug("database commit successful.")
                return 0
        return -1

class Database(object):

    def __init__(self,conn):
        self.conn = conn
        
    def close(self):
        self.conn._close()
                
class PhDatabase(Database):
    '''
    Example:
    >>> phdb = PhDatabase(MysqlConnection('testdb','54.187.112.65','root','lymanDelmedio123'))
    >>> phdb.conn._execute("DROP TABLE subscriber_articleEvent")
    0
    >>> phdb.conn._execute("DROP TABLE subscriber_article")
    0
    >>> phdb.conn._execute("DROP TABLE author")
    0
    >>> phdb.conn._execute("DROP TABLE article")
    0
    >>> phdb.conn._execute("DROP TABLE interest")
    0
    >>> phdb.conn._execute("DROP TABLE subscriber")
    0
    >>> phdb.createTableArticle()
    0
    >>> phdb.createTableAuthor()
    0
    >>> phdb.createTableSubscriber()
    0
    >>> phdb.createTableInterest()
    0
    >>> phdb.createTableSubscriber_Article()
    0
    >>> phdb.createTableSubscriber_ArticleEvent()
    0
    >>> phdb.conn._execute('DELETE FROM Dict')
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
    >>> _,res = phdb.selectDistinct('Dict',['k','v'])
    >>> print res
    (('Zhi', '32'), ('Hu', '28'), ('Russ', '31'), ('Lala', '31'), ('Franklin', '31'), ('Yang', '31'))
    >>> phdb.close()
    '''

    def createTables(self):
        self.createTableArticle()
        self.createTableAuthor()
        self.createTableSubscriber()
        self.createTableInterest()
        self.createTableSubscriber_Article()
        self.createTableSubscriber_ArticleEvent()
        'add all the table creation funcs...'
    
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
        logging.debug('query:\n'+query)
        if self.conn:
            return self.conn._execute(query)
        return -1

    def createTableAuthor(self):
        query='''CREATE TABLE author(
                authorId INT NOT NULL AUTO_INCREMENT COMMENT 'lowest authorId for an article is the first author; vice versa.',
                articleId INT NOT NULL,
                ForeName VARCHAR(255),
                Initials VARCHAR(255),
                LastName VARCHAR(255),
                Affiliation TEXT,
                PRIMARY KEY (authorId),
                FOREIGN KEY (articleId) REFERENCES article(articleId),
                CONSTRAINT uc_author_article UNIQUE (articleId,ForeName,LastName)
                );
        '''
        logging.debug('query:\n'+query)
        if self.conn:
            return self.conn._execute(query)
        return -1

    def createTableSubscriber(self):
        query='''CREATE TABLE subscriber(
            subscriberId INT NOT NULL AUTO_INCREMENT,
            firstName VARCHAR(255),
            lastName VARCHAR(255),
            email VARCHAR(255) NOT NULL,
            PRIMARY KEY (subscriberId),
            CONSTRAINT uc_email UNIQUE (email)
            );
        '''
        logging.debug('query:\n'+query)
        if self.conn:
            return self.conn._execute(query)
        return -1

    def createTableInterest(self):
        query='''CREATE TABLE interest(
                InterestId INT NOT NULL AUTO_INCREMENT,
                subscriberId INT NOT NULL,
                category TINYINT NOT NULL COMMENT 'category: 0 - area, 1- general_journal, 2 - expert_journal, 3 - keyword, 4 - author, ...',
                phrase VARCHAR(255) NOT NULL,
                PRIMARY KEY (interestId),
                FOREIGN KEY (subscriberId) REFERENCES subscriber(subscriberId),
                CONSTRAINT uc_subscriber_category_phrase UNIQUE (subscriberId, category, phrase)
                );
        '''
        logging.debug('query:\n'+query)
        if self.conn:
            return self.conn._execute(query)
        return -1    

    def createTableSubscriber_Article(self):
        query='''CREATE TABLE subscriber_article(
                subscriber_articleId INT NOT NULL AUTO_INCREMENT,
                subscriberId INT NOT NULL,
                articleId INT NOT NULL,
                PRIMARY KEY (subscriber_articleId),
                FOREIGN KEY (subscriberId) REFERENCES subscriber(subscriberId),
                FOREIGN KEY (articleId) REFERENCES article(articleId),
                CONSTRAINT uc_subscriber_article UNIQUE (subscriberId,articleId)
                );
        '''
        logging.debug('query:\n'+query)
        if self.conn:
            return self.conn._execute(query)
        return -1
    
    def createTableSubscriber_ArticleEvent(self):
        query='''CREATE TABLE subscriber_articleEvent(
                subscriber_articleEventId INT NOT NULL AUTO_INCREMENT,
                subscriber_articleId INT NOT NULL,
                timestamp DATETIME NOT NULL,
                category TINYINT NOT NULL COMMENT 'category: 0 - created, 1 - pinned, 2 - mored, 3 - viewed, ...',
                status BOOLEAN NOT NULL,
                PRIMARY KEY (subscriber_articleEventId),
                FOREIGN KEY (subscriber_articleId) REFERENCES subscriber_article(subscriber_articleId)
                );
        '''
        logging.debug('query:\n'+query)
        if self.conn:
            return self.conn._execute(query)
        return -1
    
    def insertOneReturnLastInsertId(self,tableName,d):
        '''
        Insert one record and return the last insert id (MySQL LAST_INSERT_ID()
        method). Return: -1 if the operation fails, the ID otherwise.
        The input dict must contains a key corresponding to a field with
        AUTO_INCREMENT property in the table tableName.
        
        Example:
        >>> phdb = PhDatabase(MysqlConnection('testdb','54.187.112.65','root','lymanDelmedio123'))
        >>> phdb.conn._execute("DROP TABLE subscriber_articleEvent")
        0
        >>> phdb.conn._execute("DROP TABLE subscriber_article")
        0
        >>> phdb.conn._execute("DROP TABLE interest")
        0
        >>> phdb.conn._execute("DROP TABLE subscriber")
        0
        >>> phdb.createTableSubscriber()
        0
        >>> phdb.createTableInterest()
        0
        >>> phdb.createTableSubscriber_Article()
        0
        >>> phdb.createTableSubscriber_ArticleEvent()
        0
        >>> dSubscriber1 = {'subscriberId':None,'firstName':'Franklin', 'lastName':'Zhong', 'email':'franklin.zhong@gmail.com'}
        >>> phdb.insertOneReturnLastInsertId('subscriber',dSubscriber1)
        1L
        >>> dSubscriber2 = {'subscriberId':None,'firstName':'Zhi', 'lastName':'Li', 'email':'henrylee18@yahoo.com'}
        >>> phdb.insertOneReturnLastInsertId('subscriber',dSubscriber2)
        2L
        >>> phdb.close()
        '''
        ret = self.insertMany(tableName,[d,])
        if ret != 0:
            return -1
        ret, res = self.conn._fetchall("SELECT LAST_INSERT_ID()")
        if ret !=0:
            return -1
        return res[0][0]
    
    def insertOne(self,tableName,d):
        return self.insertMany(tableName,[d,])
    
    def insertMany(self,tableName,listDict):
        '''
        conn._execute('INSERT INTO Dict (k, v) VALUES (%s, %s)', ("Hu", "28"))
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
            
            logging.debug('query:\n'+query)
            
            fields = tuple(d.values())
            if self.conn:
                ret = self.conn._execute(query,fields)
                if ret == 0:
                    nSuccessful += 1

        r = self.conn._commit()
        if r == 0:
            if nSuccessful == len(listDict):
                logging.info('%d of %d records inserted into %s successfully.' \
                              % (nSuccessful, len(listDict), tableName))
                return 0
            else: 
                logging.warning('%d of %d inserted into %s successfully.' \
                              % (nSuccessful, len(listDict), tableName))
                return 1
        else:
            logging.warning('insertMany commit failed.')
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
                
        logging.debug('query:\n'+query)
        
        ret, res = self.conn._fetchall(query)
        
        logging.debug('fetched result:\n'+ pprint.pformat(res))
        
        return (ret, res)
                        
if __name__ == '__main__':
    import doctest
    print doctest.testmod()
