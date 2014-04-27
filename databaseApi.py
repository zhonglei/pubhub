'''
Created on Apr 25, 2014

@author: zhil2
'''

import MySQLdb
import logging
import pprint

# logging.basicConfig(format='%(name)s %(levelname)s: %(message)s',
#                     level=logging.DEBUG)

class DbConnection(object):
    
    def __init__(self, n, h='localhost', u='root', p=''):
        self.dbName = n
        self.host = h
        self.user = u
        self.password = p
        self.conn = None
        
    def close(self):
        if self.conn:
            self.conn.close()
            return 0
        return -1
                                             
class MysqlConnection(DbConnection):

    '''
    Example:
    >>> conn = MysqlConnection('testdb','54.187.112.65','root','lymanDelmedio123')
    >>> conn.execute('INSERT INTO Dict (k, v) VALUES (%s,%s)', ("Zhi","32"))
    0
    >>> conn.execute('INSERT INTO Dict (k, v) VALUES (%s,%s)', ("Hu","28"))
    0
    >>> conn.execute('INSERT INTO Dict (k, v) VALUES (%s,%s)', ("Russ","31"))
    0
    >>> conn.commit()
    0
    >>> _,ret = conn.fetchall('SELECT DISTINCT k FROM Dict')
    >>> print ret
    (('Zhi',), ('Hu',), ('Russ',), ('Lala',), ('Franklin',), ('Yang',))
    >>> conn.close()
    0
    '''
#     >>> conn.execute('CREATE TABLE Dict (k VARCHAR(255), v VARCHAR(255));')
#     0

    def __init__(self, n, h, u, p):
        super(MysqlConnection,self).__init__(n,h,u,p)
        try:
            self.conn = MySQLdb.connect(self.host,self.user,self.password,self.dbName)
        except MySQLdb.Error as e:
            logging.warning(e)
        except Exception as e:
            logging.warning(e)        
    
    def execute(self,query,fields=None):
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

    def fetchall(self,query,fields=None):
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
        
    def commit(self):
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
        self.conn.close()
                
class PhDatabase(Database):
    '''
    Example:
    >>> phdb = PhDatabase(MysqlConnection('testdb','54.187.112.65','root','lymanDelmedio123'))
    >>> phdb.conn.execute("DROP TABLE author")
    0
    >>> phdb.conn.execute("DROP TABLE article")
    0
    >>> phdb.createTableArticle()
    0
    >>> phdb.createTableAuthor()
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
            return self.conn.execute(query)
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
            return self.conn.execute(query)
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
            return self.conn.execute(query)
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
            return self.conn.execute(query)
        return -1    
    
    def insertMany(self,tableName,listDict):
        '''
        conn.execute('INSERT INTO Dict (k, v) VALUES (%s, %s)', ("Hu", "28"))
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
                ret = self.conn.execute(query,fields)
                if ret == 0:
                    nSuccessful += 1

        r = self.conn.commit()
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
    
    def selectDistinct(self,tableName,columns):
        '''
        SELECT DISTINCT k, v FROM Dict
        '''
        query = 'SELECT DISTINCT '
        for c in columns[:-1]:
            query += c + ', '
        query += columns[-1] + ' '
        query += 'FROM '+tableName
         
        logging.debug('query:\n'+query)        
        ret, res = self.conn.fetchall(query)
        
        logging.debug('fetched result:\n'+ pprint.pformat(res))
        
        return (ret, res)
    
    def replaceKeyValuePair(self, listDict, tableName, keyOld, keyNew):
        '''
        Replace a old key-value pair (keyOld) in a dictionary list (listDict)
        with a new pair (keyNew), based on the old/new key lookup in a database
        table (tableName). Commonly used because there are many cases one needs 
        to lookup the id column of a table based on another column (for example, 
        look up and replace PMID with articleId in table article).
        '''
        return 0
    
    def constructPubmedQueryList(self):
        '''
        Return a list of Pubmed queries and their corresponding subscriberIds 
        based on information in the interest table.
        Rules to construct the list:
        1) All categorized as general_journal (category = 1) should be queried 
        with no specific keyword.
        2) All categorized as expert_journal (category = 2) should be queried 
        with keywords (category = 3) for a specific subscriber.
        category: 0 - area, 1- general_journal, 2 - expert_journal, 3 - keyword, 
        4 - author
        '''
        return 0
                        
if __name__ == '__main__':
    import doctest
    print doctest.testmod()
