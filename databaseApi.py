'''
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
    >>> phdb.insertMany('Dict',[{'k':'Lala','v':'31'},{'k':'Franklin','v':'31'},{'k':'Yang','v':'31'}])
    0
    >>> _,res = phdb.selectDistinct('Dict',['k','v'])
    >>> print res
    (('Zhi', '32'), ('Hu', '28'), ('Russ', '31'), ('Lala', '31'), ('Franklin', '31'), ('Yang', '31'))
    
    >>> ldSubscriber = [
    ...                {'firstName':'Franklin', 'lastName':'Zhong', 'email':'franklin.zhong@gmail.com'}, 
    ...                {'firstName':'Zhi', 'lastName':'Li', 'email':'henrylee18@yahoo.com'}, 
    ...                ]
    >>> ldInterest = [
    ...             {'subscriberId':'1', 'category':'0', 'phrase':'biochemistry'}, 
    ...                {'subscriberId':'1', 'category':'0', 'phrase':'cell biology'}, 
    ...                {'subscriberId':'1', 'category':'1', 'phrase':'Nature'}, 
    ...                {'subscriberId':'1', 'category':'1', 'phrase':'Science'}, 
    ...                {'subscriberId':'1', 'category':'1', 'phrase':'Cell'}, 
    ...                {'subscriberId':'1', 'category':'2', 'phrase':'Molecular Cell'}, 
    ...                {'subscriberId':'1', 'category':'2', 'phrase':'Nature structural and Molecular Biology'}, 
    ...                {'subscriberId':'1', 'category':'2', 'phrase':'Molecular and Cellular Biology'}, 
    ...                {'subscriberId':'1', 'category':'3', 'phrase':'telomerase and cancer biology'}, 
    ...                {'subscriberId':'1', 'category':'3', 'phrase':'telomere and DNA replication'}, 
    ...                {'subscriberId':'2', 'category':'0', 'phrase':'biochemistry'}, 
    ...                {'subscriberId':'2', 'category':'0', 'phrase':'Immunology'}, 
    ...                {'subscriberId':'2', 'category':'1', 'phrase':'Nature'}, 
    ...                {'subscriberId':'2', 'category':'1', 'phrase':'Science'}, 
    ...                {'subscriberId':'2', 'category':'2', 'phrase':'Immunity'}, 
    ...                {'subscriberId':'2', 'category':'2', 'phrase':'Journal of Immunology'}, 
    ...                {'subscriberId':'2', 'category':'2', 'phrase':'Molecular Cell'}, 
    ...                {'subscriberId':'2', 'category':'2', 'phrase':'Nature structural and Molecular Biology'}, 
    ...                {'subscriberId':'2', 'category':'3', 'phrase':'noncoding RNA'}, 
    ...                ]
    >>> phdb.insertMany('subscriber', ldSubscriber)
    0
    >>> phdb.insertMany('interest', ldInterest)
    0
    >>> ld = [{'k':'Zhi', 'x':'y'},{'k':'Franklin', 'z':'w'}]
    >>> phdb.replaceKeyValuePair(ld, 'Dict', 'k', 'v')
    0
    >>> ld
    [{'x': 'y', 'v': '32'}, {'z': 'w', 'v': '31'}]
    >>> phdb.constructPubmedQueryList()
    [('("Cell"[Journal])', [1L]), ('("Nature"[Journal])', [1L, 2L]), ('("Science"[Journal])', [1L, 2L]), ('(telomerase and cancer biology) AND ("Cell"[Journal] OR "Nature"[Journal] OR "Science"[Journal] OR "Molecular and Cellular Biology"[Journal] OR "Molecular Cell"[Journal] OR "Nature structural and Molecular Biology"[Journal] )', [1L]), ('(telomere and DNA replication) AND ("Cell"[Journal] OR "Nature"[Journal] OR "Science"[Journal] OR "Molecular and Cellular Biology"[Journal] OR "Molecular Cell"[Journal] OR "Nature structural and Molecular Biology"[Journal] )', [1L]), ('(noncoding RNA) AND ("Nature"[Journal] OR "Science"[Journal] OR "Immunity"[Journal] OR "Journal of Immunology"[Journal] OR "Molecular Cell"[Journal] OR "Nature structural and Molecular Biology"[Journal] )', [2L])]
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
    
    def replaceKeyValuePair(self, listDict, tableName, keyOld, keyNew):
        '''
        Replace a old key-value pair (with key keyOld) in a list of dictionaries 
        (listDict) with a new pair (with key keyNew), based on the old/new key 
        lookup in a database table (tableName). Commonly used because there are 
        many cases one needs to lookup and replace the id column of a table 
        based on another column (for example, look up and replace PMID with 
        articleId in table article).
        '''
        _,res = self.selectDistinct(tableName, [keyOld, keyNew])
        dictKeyOld2New = dict(map(str, x) for x in res) # map everything to string
        rf = 0
        for d in listDict:
            try:
                d[keyNew] = dictKeyOld2New[d[keyOld]]
                d.pop(keyOld,None)
            except Exception as e:
                logging.warning(e)
                rf = 1                
            logging.debug(d)
            
        return rf
    
    def constructPubmedQueryList(self):
        '''
        Return a list of Pubmed queries and their corresponding subscriberIds 
        based on information in the interest table.
        Rules to construct the list:
        1) All categorized as general_journal (category = 1) should be queried 
        with no specific keyword. e.g. Nature[Journal]
        2) All categorized as expert_journal (category = 2) should be queried 
        with keywords (category = 3) for a specific subscriber.
        category: 0 - area, 1- general_journal, 2 - expert_journal, 3 - keyword, 
        4 - author
        Example: (telomerase) AND ("Nature"[Jour] OR "Nature medicine"[Jour] )
        '''
#         +------------+--------------+----------+-----------------------------------------+
#         | InterestId | subscriberId | category | phrase                                  |
#         +------------+--------------+----------+-----------------------------------------+
#         |          1 |            1 |        0 | biochemistry                            |
#         |          2 |            1 |        0 | cell biology                            |
#         |          5 |            1 |        1 | Cell                                    |
#         |          3 |            1 |        1 | Nature                                  |
#         |          4 |            1 |        1 | Science                                 |
#         |          8 |            1 |        2 | Molecular and Cellular Biology          |
#         |          6 |            1 |        2 | Molecular Cell                          |
#         |          7 |            1 |        2 | Nature structural and Molecular Biology |
#         |          9 |            1 |        3 | telomerase and cancer biology           |
#         |         10 |            1 |        3 | telomere and DNA replication            |
#         |         11 |            2 |        0 | biochemistry                            |
#         |         12 |            2 |        0 | Immunology                              |
#         |         13 |            2 |        1 | Nature                                  |
#         |         14 |            2 |        1 | Science                                 |
#         |         15 |            2 |        2 | Immunity                                |
#         |         16 |            2 |        2 | Journal of Immunology                   |
#         |         17 |            2 |        2 | Molecular Cell                          |
#         |         18 |            2 |        2 | Nature structural and Molecular Biology |
#         |         19 |            2 |        3 | noncoding RNA                           |
#         +------------+--------------+----------+-----------------------------------------+        

        list=[]
        
        _, generalJournals = self.selectDistinct('interest', ['phrase',], 
                                                 'category = 1')
        generalJournals = singleStrip(generalJournals)    
            
        for j in generalJournals:
            query = r'("%s"[Journal])' % j
            
            _, subscribers = self.selectDistinct('interest',['subscriberId',], 
                                                 "phrase = '%s'" % j)
            subscribers = singleStrip(subscribers)
            
            logging.debug('query: '+query)
            logging.debug('subscribers: '+str(subscribers))
            
            list.append((query, subscribers))
            
        'FIXME: can have less number of db queries'
        
        _, subscriberIds = self.selectDistinct('interest', ['subscriberId',])
        subscriberIds = singleStrip(subscriberIds)    
           
        for i in subscriberIds:
            
            _, keywords = self.selectDistinct('interest', ['phrase'], 
                                    'subscriberId = %d AND category = 3' % i)
            keywords = singleStrip(keywords)
            
            _, subscriberGeneralJournals = self.selectDistinct('interest', 
                        ['phrase',], 'subscriberId = %d AND category = 1' % i)
            subscriberGeneralJournals = singleStrip(subscriberGeneralJournals)
            
            _, subscriberExpertJournals = self.selectDistinct('interest', 
                        ['phrase',], 'subscriberId = %d AND category = 2' % i)
            subscriberExpertJournals = singleStrip(subscriberExpertJournals)
            
            subscriberJournals = subscriberGeneralJournals + subscriberExpertJournals
            
            for k in keywords:
                query = r"(%s) AND (" % k
                for j in subscriberJournals[:-1]:
                    query += r'"%s"[Journal] OR ' % j
                query += r'"%s"[Journal] )' % subscriberJournals[-1]
                
                logging.debug('query: '+query)

                subscribers = [i]
                list.append((query, subscribers))
                
        logging.debug('constructed Pubmed query list:\n'+ pprint.pformat(list))
                
        return list
    
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
