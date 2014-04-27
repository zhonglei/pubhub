'''
Created on Apr 26, 2014

@author: zhil2
'''

from pubmedApi import PubmedApi
from databaseApi import PhDatabase, MysqlConnection
import logging

logging.basicConfig(format='%(name)s %(levelname)s: %(message)s',
                    level=logging.INFO)

if __name__ == '__main__':
    
     
    '================================'
    'create subscriber query'
    '================================'
     
#     'connect pubhub database'    
#     phdb = PhDatabase(MysqlConnection('pubhub', '54.187.112.65', 'root', 'lymanDelmedio123'))    
#      
#     'create tables and populate dummy subscribers'
#     '''
#     subscriber:    
#     +--------------+--------------+------+-----+---------+----------------+
#     | Field        | Type         | Null | Key | Default | Extra          |
#     +--------------+--------------+------+-----+---------+----------------+
#     | subscriberId | int(11)      | NO   | PRI | NULL    | auto_increment |
#     | firstName    | varchar(255) | YES  |     | NULL    |                |
#     | lastName     | varchar(255) | YES  |     | NULL    |                |
#     | email        | varchar(255) | NO   | UNI | NULL    |                |
#     +--------------+--------------+------+-----+---------+----------------+
#     interest:
#     +--------------+--------------+------+-----+---------+----------------+
#     | Field        | Type         | Null | Key | Default | Extra          |
#     +--------------+--------------+------+-----+---------+----------------+
#     | InterestId   | int(11)      | NO   | PRI | NULL    | auto_increment |
#     | subscriberId | int(11)      | NO   | MUL | NULL    |                |
#     | category*    | tinyint(4)   | NO   |     | NULL    |                |
#     | phrase       | varchar(255) | NO   |     | NULL    |                |
#     +--------------+--------------+------+-----+---------+----------------+
#     '*category: 0 - area, 1- general_journal, 2 - expert_journal, 3 - keyword, 4 - author'
#     '''
#     phdb.createTableSubscriber()
#     phdb.createTableInterest()
#     ldSubscriber = [
#                     {'firstName':'Franklin', 'lastName':'Zhong', 'email':'franklin.zhong@gmail.com'}, 
#                     {'firstName':'Zhi', 'lastName':'Li', 'email':'henrylee18@yahoo.com'}, 
#                     ]
#     ldInterest = [
#                     {'subscriberId':'1', 'category':'0', 'phrase':'biochemistry'}, 
#                     {'subscriberId':'1', 'category':'0', 'phrase':'cell biology'}, 
#                     {'subscriberId':'1', 'category':'1', 'phrase':'Nature'}, 
#                     {'subscriberId':'1', 'category':'1', 'phrase':'Science'}, 
#                     {'subscriberId':'1', 'category':'1', 'phrase':'Cell'}, 
#                     {'subscriberId':'1', 'category':'2', 'phrase':'Molecular Cell'}, 
#                     {'subscriberId':'1', 'category':'2', 'phrase':'Nature structural and Molecular Biology'}, 
#                     {'subscriberId':'1', 'category':'2', 'phrase':'Molecular and Cellular Biology'}, 
#                     {'subscriberId':'1', 'category':'3', 'phrase':'telomerase and cancer biology'}, 
#                     {'subscriberId':'1', 'category':'3', 'phrase':'telomere and DNA replication'}, 
#                      
#                     {'subscriberId':'2', 'category':'0', 'phrase':'biochemistry'}, 
#                     {'subscriberId':'2', 'category':'0', 'phrase':'Immunology'}, 
#                     {'subscriberId':'2', 'category':'1', 'phrase':'Nature'}, 
#                     {'subscriberId':'2', 'category':'1', 'phrase':'Science'}, 
#                     {'subscriberId':'2', 'category':'2', 'phrase':'Immunity'}, 
#                     {'subscriberId':'2', 'category':'2', 'phrase':'Journal of Immunology'}, 
#                     {'subscriberId':'2', 'category':'2', 'phrase':'Molecular Cell'}, 
#                     {'subscriberId':'2', 'category':'2', 'phrase':'Nature structural and Molecular Biology'}, 
#                     {'subscriberId':'2', 'category':'3', 'phrase':'noncoding RNA'}, 
#  
#                     ]
#     phdb.insertMany('subscriber', ldSubscriber)
#     phdb.insertMany('interest', ldInterest)
#      
#      
#     'close pubhub database'    
#     phdb.close()
    
    
    
    '================================'
    'query pubmed and store in pubhub'
    '================================'
    
#     queryStr = 'Nature[Journal]+AND+(2010/11/01[PDAT]+:+2012/11/12[PDAT])'
#     queryStr = 'Nature[Journal]+AND+(2008/11/01[PDAT]+:+2012/11/12[PDAT])'
#     queryStr = 'Science[Journal]+AND+(2008/11/01[PDAT]+:+2012/11/12[PDAT])'
#     queryStr = 'Science[Journal]+AND+(2005/07/01[PDAT]+:+2010/07/12[PDAT])'
#     queryStr = 'Cell[Journal]+AND+(2008/07/01[PDAT]+:+2010/07/12[PDAT])'
#     queryStr = 'Nature[Journal]+AND+(2012/07/01[PDAT]+:+2012/07/12[PDAT])'
#     queryStr = 'Molecular+Cell[Journal]+AND+(2010/05/01[PDAT]+:+2010/07/12[PDAT])'
#     queryStr = 'Molecular+and+cellular+biology[Journal]+AND+(2010/05/01[PDAT]+:+2011/07/12[PDAT])'
    queryStr = '(telomere+and+DNA+replication)+AND+(2010/05/01[PDAT]+:+2011/07/12[PDAT])'
          
    'query pubmed'
    pa = PubmedApi()
    ldArticle, ldAuthor = pa.query(queryStr, 10)
  
    'connect pubhub database'    
    phdb = PhDatabase(MysqlConnection('pubhub', '54.187.112.65', 'root', 'lymanDelmedio123'))    
      
    'record article'
    phdb.insertMany('article', ldArticle)    
  
    'record author'
    #Need to look up articleId in article, replace key PMID with articleID

    
    _,res = phdb.selectDistinct('article',['PMID','articleId'])    
    dictPmid2Articleid = dict(res)
    for d in ldAuthor:
        d['articleId'] = dictPmid2Articleid[long(d['PMID'])]
        d.pop('PMID',None)
        logging.debug(d)

    phdb.insertMany('author', ldAuthor)
  
    'close pubhub database'    
    phdb.close()
    
    '================================'
    'done'
    '================================'
    
    logging.info('\n\nDone.\n')

    
    
    
    
    