'''

Pubhub's main controller logic for the interaction between the Pubhub database,
the Pubmed database and the front-end Bottle web server.

Created on Apr 26, 2014

@author: zhil2
'''

import MySQLdb
import urllib2
from bottle import template
from logging import warning, debug, info
import pprint
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from phTools import singleStrip, replaceKeyValuePair
from phInfo import webServerInfo
from pubmedApi import PubmedApi
from phDatabaseApi import PhDatabase, MysqlConnection, createMysqlDatetimeStr
from phDatabaseApi import dbBoolean, Subscriber_ArticleEventCategory, \
                            InterestCategory

'''
format '%(asctime)s %(name)s %(levelname)s: %(message)s'
level DEBUG, INFO
'''
# import logging
# logging.basicConfig(format='%(name)s %(levelname)s: %(message)s',
#                     level=logging.DEBUG)

def createPubmedQueryList(phdb, subscriberIdIn = None):
    '''
    Return a list of Pubmed queries and their corresponding subscriberIds 
    based on information in the interest table of database phdb.
    
    If subscriberIdIn is not provided, construct a list for all subscribers;
    otherwise, the list is only for the subscriber specified.
    
    Rules to construct the list:
    1) All categorized as generalJournal should be queried 
    with no specific keyword. e.g. Nature[Journal]
    2) All categorized as expertJournal should be queried 
    with keywords for a specific subscriber.
    e.g.: (telomerase) AND ("Nature"[Journal] OR "Nature medicine"[Journal] )    
                
    Example:
    >>> from phInfo import doctestDbInfo
    >>> phdb = PhDatabase(MysqlConnection(doctestDbInfo['dbName'],doctestDbInfo['ip'],doctestDbInfo['user'],doctestDbInfo['password']))
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
    >>> ldSubscriber = [
    ...                {'firstName':'Franklin', 'lastName':'Zhong', 'email':'franklin.zhong@gmail.com'}, 
    ...                {'firstName':'Zhi', 'lastName':'Li', 'email':'henrylee18@yahoo.com'}, 
    ...                ]
    >>> ldInterest = [
    ...             {'subscriberId':'1', 'category':'0', 'phrase':'biochemistry'}, 
    ...                {'subscriberId':'1', 'category':'1', 'phrase':'cell biology'}, 
    ...                {'subscriberId':'1', 'category':'2', 'phrase':'Nature'}, 
    ...                {'subscriberId':'1', 'category':'2', 'phrase':'Science'}, 
    ...                {'subscriberId':'1', 'category':'2', 'phrase':'Cell'}, 
    ...                {'subscriberId':'1', 'category':'3', 'phrase':'Molecular Cell'}, 
    ...                {'subscriberId':'1', 'category':'3', 'phrase':'Nature structural and Molecular Biology'}, 
    ...                {'subscriberId':'1', 'category':'3', 'phrase':'Molecular and Cellular Biology'}, 
    ...                {'subscriberId':'1', 'category':'4', 'phrase':'telomerase and cancer biology'}, 
    ...                {'subscriberId':'1', 'category':'4', 'phrase':'telomere and DNA replication'}, 
    ...                {'subscriberId':'2', 'category':'1', 'phrase':'biochemistry'}, 
    ...                {'subscriberId':'2', 'category':'1', 'phrase':'Immunology'}, 
    ...                {'subscriberId':'2', 'category':'2', 'phrase':'Nature'}, 
    ...                {'subscriberId':'2', 'category':'2', 'phrase':'Science'}, 
    ...                {'subscriberId':'2', 'category':'3', 'phrase':'Immunity'}, 
    ...                {'subscriberId':'2', 'category':'3', 'phrase':'Journal of Immunology'}, 
    ...                {'subscriberId':'2', 'category':'3', 'phrase':'Molecular Cell'}, 
    ...                {'subscriberId':'2', 'category':'3', 'phrase':'Nature structural and Molecular Biology'}, 
    ...                {'subscriberId':'2', 'category':'4', 'phrase':'noncoding RNA'}, 
    ...                ]
    >>> phdb.insertMany('subscriber', ldSubscriber)
    0
    >>> phdb.insertMany('interest', ldInterest)
    0
    >>> createPubmedQueryList(phdb)
    [(u'(biology OR medical OR neuroscience OR gene OR brain) AND ("Cell"[Journal])', [1L], u'Cell'), (u'(biology OR medical OR neuroscience OR gene OR brain) AND ("Nature"[Journal])', [1L, 2L], u'Nature'), (u'(biology OR medical OR neuroscience OR gene OR brain) AND ("Science"[Journal])', [1L, 2L], u'Science'), (u'(telomerase and cancer biology) AND ("Cell"[Journal] OR "Nature"[Journal] OR "Science"[Journal] OR "Molecular and Cellular Biology"[Journal] OR "Molecular Cell"[Journal] OR "Nature structural and Molecular Biology"[Journal] )', [1L], u'telomerase and cancer biology'), (u'(telomere and DNA replication) AND ("Cell"[Journal] OR "Nature"[Journal] OR "Science"[Journal] OR "Molecular and Cellular Biology"[Journal] OR "Molecular Cell"[Journal] OR "Nature structural and Molecular Biology"[Journal] )', [1L], u'telomere and DNA replication'), (u'(noncoding RNA) AND ("Nature"[Journal] OR "Science"[Journal] OR "Immunity"[Journal] OR "Journal of Immunology"[Journal] OR "Molecular Cell"[Journal] OR "Nature structural and Molecular Biology"[Journal] )', [2L], u'noncoding RNA')]
    >>> createPubmedQueryList(phdb, 1L)
    [(u'(biology OR medical OR neuroscience OR gene OR brain) AND ("Cell"[Journal])', [1L], u'Cell'), (u'(biology OR medical OR neuroscience OR gene OR brain) AND ("Nature"[Journal])', [1L], u'Nature'), (u'(biology OR medical OR neuroscience OR gene OR brain) AND ("Science"[Journal])', [1L], u'Science'), (u'(telomerase and cancer biology) AND ("Cell"[Journal] OR "Nature"[Journal] OR "Science"[Journal] OR "Molecular and Cellular Biology"[Journal] OR "Molecular Cell"[Journal] OR "Nature structural and Molecular Biology"[Journal] )', [1L], u'telomerase and cancer biology'), (u'(telomere and DNA replication) AND ("Cell"[Journal] OR "Nature"[Journal] OR "Science"[Journal] OR "Molecular and Cellular Biology"[Journal] OR "Molecular Cell"[Journal] OR "Nature structural and Molecular Biology"[Journal] )', [1L], u'telomere and DNA replication')]
    >>> phdb.close()
    '''
    
    listQuery=[]
    
    if subscriberIdIn is None:
        _, generalJournals = phdb.selectDistinct('interest', ['phrase',], 
                        'category = %s' % str(InterestCategory.generalJournal)) #generalJournal
    else:
        _, generalJournals = phdb.selectDistinct('interest', ['phrase',], 
                        'category = %s and subscriberId = %s'
                        % (InterestCategory.generalJournal, str(subscriberIdIn)))
        
    generalJournals = singleStrip(generalJournals)    
        
    for j in generalJournals:
        
        query = ''

        'for biology-related field, add filter'
        query += r'(biology OR medical OR neuroscience OR gene OR brain) AND '
        
        query += r'("%s"[Journal])' % j
        
        if subscriberIdIn is None:
            _, subscribers = phdb.selectDistinct('interest',['subscriberId',], 
                                                 "phrase = '%s'" % j)
            subscribers = singleStrip(subscribers)
        else:
            subscribers = [subscriberIdIn,]
        
        debug('query: '+query)
        debug('subscribers: '+str(subscribers))
        
        listQuery.append((query, subscribers, j))
        
    'FIXME: can have less number of db queries'

    if subscriberIdIn is None:    
        _, subscriberIds = phdb.selectDistinct('interest', ['subscriberId',])
        subscriberIds = singleStrip(subscriberIds)    
    else:
        subscriberIds = [subscriberIdIn,]
       
    for i in subscriberIds:
        
        _, keywords = phdb.selectDistinct('interest', ['phrase'], 
                                'subscriberId = %d AND category = %s' % (i, str(InterestCategory.keyword))) #keyword
        keywords = singleStrip(keywords)
        
        _, subscriberGeneralJournals = phdb.selectDistinct('interest', 
                    ['phrase',], 'subscriberId = %d AND category = %s' % (i, str(InterestCategory.generalJournal))) #generalJournal
        subscriberGeneralJournals = singleStrip(subscriberGeneralJournals)
        
        _, subscriberExpertJournals = phdb.selectDistinct('interest', 
                    ['phrase',], 'subscriberId = %d AND category = %s' % (i, str(InterestCategory.expertJournal))) #expertJournal
        subscriberExpertJournals = singleStrip(subscriberExpertJournals)
        
        subscriberJournals = subscriberGeneralJournals + subscriberExpertJournals
        
        for k in keywords:
            query = r"(%s) AND (" % k
            for j in subscriberJournals[:-1]:
                query += r'"%s"[Journal] OR ' % j
            query += r'"%s"[Journal] )' % subscriberJournals[-1]
            
            debug('query: '+query)

            subscribers = [i]
            
            listQuery.append((query, subscribers, k))
            
    debug('constructed Pubmed query list:\n'+ pprint.pformat(listQuery))
            
    return listQuery

def createPubmedTimeStr(startTime, endTime):
    '''
    Example:
    >>> createPubmedTimeStr(1398036175.4, 1399531966.5)
    '(2014/04/20[PDAT] : 2014/05/08[PDAT])'
    '''
    startT = time.strftime('%Y/%m/%d[PDAT]', time.gmtime(startTime))
    endT = time.strftime('%Y/%m/%d[PDAT]', time.gmtime(endTime))
    return '(' + startT + ' : ' + endT + ')'

def createDayStr(DateCreated, now = None):
    '''
    DateCreated and now are in format of datetime.
    
    Example:
    >>> from datetime import datetime
    >>> createDayStr(datetime.fromtimestamp(1398036175), datetime.fromtimestamp(1399531966))
    '17 days ago'
    >>> createDayStr(datetime.fromtimestamp(1399531960), datetime.fromtimestamp(1399531966))
    'Today'
    >>> createDayStr(datetime.fromtimestamp(1399531960 - 3600*24), datetime.fromtimestamp(1399531966))
    '1 day ago'
    '''
    if now is None:
        now = time.time()
    else:
        now = int(now.strftime('%s'))
    daysElapsed = int((now-int(DateCreated.strftime('%s')))/24/3600)
    if daysElapsed == 0:
        dayStr = 'Today'
    elif daysElapsed == 1:
        dayStr = '1 day ago'
    else:
        dayStr = '%d days ago' % daysElapsed

    return dayStr

def createAuthorStr(listFirstLastAuthorName):
    '''
    Example:
    >>> createAuthorStr([('Z','Li'), ('F','Zhong')])
    'Z Li and F Zhong'
    >>> createAuthorStr([('Z','Li'), ('F','Zhong'), ('JX', 'Li')])
    'Z Li, F Zhong and JX Li'
    >>> createAuthorStr([('Z','Li'),])
    'Z Li'
    >>> createAuthorStr([('','Li'),])
    'Li'
    >>> createAuthorStr([('','Li'), ('F','Zhong')])
    'Li and F Zhong'
    '''

    authorStr = ''
    for a in listFirstLastAuthorName[:-2]:
        if a[0] != '':
            authorStr += a[0]+' '
        if a[1] != '':
            authorStr += a[1]
        authorStr += ', '
    if len(listFirstLastAuthorName) > 1:
        a = listFirstLastAuthorName[-2]
        if a[0] != '':
            authorStr += a[0]+' '
        if a[1] != '':
            authorStr += a[1]
        authorStr += ' and '
    a = listFirstLastAuthorName[-1]
    if a[0] != '':
        authorStr += a[0]+' '
    if a[1] != '':
        authorStr += a[1]
        
    return authorStr

def queryPubmedAndStoreResults(dbInfo, queryStartTime, queryEndTime, subscriberIdIn = None):
    r'''
    If subscriberIdIn is not specified, query for all subscribers in database;
    otherwise, query for that specific subscriber only.

    Example:
    >>> from phInfo import doctestDbInfo
    >>> phdb = PhDatabase(MysqlConnection(doctestDbInfo['dbName'],doctestDbInfo['ip'],doctestDbInfo['user'],doctestDbInfo['password']))
    >>> phdb._formatDatabase()
    >>> phdb.fetchall('SELECT * FROM subscriber')
    (0, ())
    >>> phdb.fetchall('SELECT * FROM interest')
    (0, ())
    >>> phdb.close()
    >>> subscriberId = signUpSubscriber(doctestDbInfo, 'lizhi1981@gmail.com', '123', 'Zhi', 'Li', '1', ['DNA sequencing'])
    >>> print subscriberId
    1
    >>> phdb = PhDatabase(MysqlConnection(doctestDbInfo['dbName'],doctestDbInfo['ip'],doctestDbInfo['user'],doctestDbInfo['password']))
    >>> phdb.fetchall('SELECT * FROM subscriber')
    (0, ((1L, u'Zhi', u'Li', u'lizhi1981@gmail.com', u'123'),))
    >>> phdb.fetchall('SELECT * FROM interest')
    (0, ((1L, 1L, 1, u'Bioinformatics and computational genomics'), (2L, 1L, 2, u'Cell'), (3L, 1L, 2, u'Nature'), (4L, 1L, 2, u'Science'), (11L, 1L, 3, u'Cancer Cell'), (13L, 1L, 3, u'Cell Reports'), (19L, 1L, 3, u'Cell Stem Cell'), (16L, 1L, 3, u'Curr Biol.'), (23L, 1L, 3, u'Developmental Cell'), (7L, 1L, 3, u'eLife'), (18L, 1L, 3, u'EMBO J.'), (17L, 1L, 3, u'Genes & Development'), (14L, 1L, 3, u'Genome Biology'), (24L, 1L, 3, u'Genome Research'), (8L, 1L, 3, u'Molecular and Cellular Biology'), (15L, 1L, 3, u'Molecular Cell'), (6L, 1L, 3, u'Nature Biotechnology'), (28L, 1L, 3, u'Nature Cell Biology'), (20L, 1L, 3, u'Nature Communications'), (12L, 1L, 3, u'Nature Genetics'), (9L, 1L, 3, u'Nature Medicine'), (27L, 1L, 3, u'Nature Methods'), (10L, 1L, 3, u'Nature Structural & Molecular Biology'), (5L, 1L, 3, u'Nucleic Acids Res.'), (25L, 1L, 3, u'PLoS Biology'), (26L, 1L, 3, u'PLoS Computational Biology'), (22L, 1L, 3, u'PLoS Genetics'), (21L, 1L, 3, u'Proc. Natl. Acad. Sci. U.S.A.'), (29L, 1L, 4, u'DNA sequencing')))
    >>> phdb.close()
    >>> subscriberId = signUpSubscriber(doctestDbInfo, 'henrylee18@yahoo.com', '123', 'Henry', 'Lee', '5', ['telomerase'])
    >>> print subscriberId
    2
    >>> phdb = PhDatabase(MysqlConnection(doctestDbInfo['dbName'],doctestDbInfo['ip'],doctestDbInfo['user'],doctestDbInfo['password']))
    >>> phdb.fetchall('SELECT * FROM subscriber')
    (0, ((1L, u'Zhi', u'Li', u'lizhi1981@gmail.com', u'123'), (2L, u'Henry', u'Lee', u'henrylee18@yahoo.com', u'123')))
    >>> phdb.fetchall('SELECT * FROM interest')
    (0, ((1L, 1L, 1, u'Bioinformatics and computational genomics'), (2L, 1L, 2, u'Cell'), (3L, 1L, 2, u'Nature'), (4L, 1L, 2, u'Science'), (11L, 1L, 3, u'Cancer Cell'), (13L, 1L, 3, u'Cell Reports'), (19L, 1L, 3, u'Cell Stem Cell'), (16L, 1L, 3, u'Curr Biol.'), (23L, 1L, 3, u'Developmental Cell'), (7L, 1L, 3, u'eLife'), (18L, 1L, 3, u'EMBO J.'), (17L, 1L, 3, u'Genes & Development'), (14L, 1L, 3, u'Genome Biology'), (24L, 1L, 3, u'Genome Research'), (8L, 1L, 3, u'Molecular and Cellular Biology'), (15L, 1L, 3, u'Molecular Cell'), (6L, 1L, 3, u'Nature Biotechnology'), (28L, 1L, 3, u'Nature Cell Biology'), (20L, 1L, 3, u'Nature Communications'), (12L, 1L, 3, u'Nature Genetics'), (9L, 1L, 3, u'Nature Medicine'), (27L, 1L, 3, u'Nature Methods'), (10L, 1L, 3, u'Nature Structural & Molecular Biology'), (5L, 1L, 3, u'Nucleic Acids Res.'), (25L, 1L, 3, u'PLoS Biology'), (26L, 1L, 3, u'PLoS Computational Biology'), (22L, 1L, 3, u'PLoS Genetics'), (21L, 1L, 3, u'Proc. Natl. Acad. Sci. U.S.A.'), (29L, 1L, 4, u'DNA sequencing'), (30L, 2L, 1, u'Biochemistry, cell biology and molecular biology'), (31L, 2L, 2, u'Cell'), (32L, 2L, 2, u'Nature'), (33L, 2L, 2, u'Science'), (42L, 2L, 3, u'Cancer Cell'), (34L, 2L, 3, u'Cancer Research'), (44L, 2L, 3, u'Cell Reports'), (50L, 2L, 3, u'Cell Stem Cell'), (46L, 2L, 3, u'Curr Biol.'), (55L, 2L, 3, u'Developmental Cell'), (37L, 2L, 3, u'eLife'), (49L, 2L, 3, u'EMBO J.'), (48L, 2L, 3, u'Genes & Development'), (54L, 2L, 3, u'J Biol Chem.'), (38L, 2L, 3, u'Molecular and Cellular Biology'), (45L, 2L, 3, u'Molecular Cell'), (36L, 2L, 3, u'Nature Biotechnology'), (58L, 2L, 3, u'Nature Cell Biology'), (39L, 2L, 3, u'Nature Chemical Biology'), (51L, 2L, 3, u'Nature Communications'), (43L, 2L, 3, u'Nature Genetics'), (40L, 2L, 3, u'Nature Medicine'), (57L, 2L, 3, u'Nature Methods'), (41L, 2L, 3, u'Nature Structural & Molecular Biology'), (35L, 2L, 3, u'Nucleic Acids Res.'), (56L, 2L, 3, u'PLoS Biology'), (53L, 2L, 3, u'PLoS Genetics'), (52L, 2L, 3, u'Proc. Natl. Acad. Sci. U.S.A.'), (47L, 2L, 3, u'Structure'), (59L, 2L, 4, u'telomerase')))
    >>> phdb.close()
    >>> getLastPhDatabaseUpdateTime(doctestDbInfo)
    >>> queryPubmedAndStoreResults(doctestDbInfo, 1399664864 - 2 * 24 * 3600, 1399664864)
    >>> phdb = PhDatabase(MysqlConnection(doctestDbInfo['dbName'],doctestDbInfo['ip'],doctestDbInfo['user'],doctestDbInfo['password']))
    >>> phdb.selectDistinct('article',['articleId'])
    (0, ((37L,), (36L,), (35L,), (34L,), (33L,), (32L,), (31L,), (47L,), (23L,), (22L,), (30L,), (29L,), (28L,), (46L,), (21L,), (20L,), (45L,), (44L,), (27L,), (26L,), (25L,), (24L,), (51L,), (50L,), (49L,), (48L,), (43L,), (42L,), (41L,), (40L,), (39L,), (38L,), (19L,), (18L,), (17L,), (16L,), (15L,), (14L,), (13L,), (12L,), (11L,), (10L,), (9L,), (8L,), (7L,), (6L,), (5L,), (4L,), (3L,), (2L,), (1L,), (52L,)))
    >>> phdb.close()
    >>> getArticleMorePage(doctestDbInfo, 1, 7)
    u'\n<!DOCTYPE html>\n<html lang="en">\n    <head>\n        <meta http-equiv="content-type" content="text/html; charset=UTF-8"> \n        <title>Scooply -- GroEL/ES Chaperonin Modulates the Mechanism and Accelerates the Rate of TIM-Barrel Domain Folding.</title>\n        <meta name="generator" content="Bootply" />\n        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">\n        <!--Bootstrap-->\n\t\t<link href="css/bootstrap.min.css" rel="stylesheet">\n\t\t<!--Jasny-->\n\t\t  <link href="jasny-bootstrap/css/jasny-bootstrap.min.css" rel="stylesheet">\n\t\t<!--- Style sheet for this template-->\n\t\t<link href="css/scooply-v3.css" rel="stylesheet">\t\t\n        <!--[if lt IE 9]>\n          <script src="//html5shim.googlecode.com/svn/trunk/html5.js"></script>\n        <![endif]-->\n    </head>\n    \n\t<body>\t\t\t\t\t\t\n\t\t<div class="content_main">\t\n\t\t\n\t\t\t<div class="article_info">\n\t\t\t\n\t\t\t\t<h3> <b> GroEL/ES Chaperonin Modulates the Mechanism and Accelerates the Rate of TIM-Barrel Domain Folding. </b> </h3>\n\n\t\t\t\t<h4> \n\t\t\t\t\t1 day ago in <span class="label label-default">Cell</span>\n\t\t\t\t</h4>\n\n\n\t\t\t\t<p class="alignleft"> \n\t\t\t\t\t|\n\t\t\t\t\t <a href="redirect?subscriberId=1&amp;articleId=7&amp;redirectUrl=http%3A//www.ncbi.nlm.nih.gov/pubmed/24813614"> PubMed </a> |\n\t\t\t\t\t <a href="pin?subscriberId=1&amp;articleId=7&amp;status=1"> Pin </a> |\n\t\t\t\t</p>\n\t\t\t</div>\n\t\t\t<div style="clear: both;"></div>\n\t\t\t\n\t\t\t<div class="article_info">\n\t\t\t\t\t\t\n\t\t\t\t<p> <b>Abstract:</b> The GroEL/ES chaperonin system functions as a protein folding cage. Many obligate substrates of GroEL share the (??)8 TIM-barrel fold, but how the chaperonin promotes folding of these proteins is not known. Here, we analyzed the folding of DapA at peptide resolution using hydrogen/deuterium exchange and mass spectrometry. During spontaneous folding, all elements of the DapA TIM barrel acquire structure simultaneously in a process associated with a long search time. In contrast, GroEL/ES accelerates folding more than 30-fold by catalyzing segmental structure formation in the TIM barrel. Segmental structure formation is also observed during the fast spontaneous folding of a structural homolog of DapA from a bacterium that lacks GroEL/ES. Thus, chaperonin independence correlates with folding properties otherwise enforced by protein confinement in the GroEL/ES cage. We suggest that folding catalysis by GroEL/ES is required by a set of proteins to reach native state at a biologically relevant timescale, avoiding aggregation or degradation. </p>\n\n\t\t\t\t<p> <b>Authors:</b> F Georgescauld, K Popova, AJ Gupta, A Bracher, JR Engen, M Hayer-Hartl and FU Hartl </p>\n\n\t\t\t\t<p> <b>Affiliation:</b> Department of Cellular Biochemistry, Max Planck Institute of Biochemistry, Am Klopferspitz 18, 82152 Martinsried, Germany. </p>\n\t\t\t\t\n\t\t\t</div>\t\t\t\n\t\t\t<div style="clear: both;"></div>\n\n\t\t</div><!-- content_main-->\n\n    \n\t<!-- jQuery (necessary for Bootstrap\'s JavaScript plugins) -->\n    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js"></script>\n    <!-- Include all compiled plugins (below), or include individual files as needed -->\n    <script src="js/bootstrap.min.js"></script>\n\n     <!-- JavaScript jQuery code from Bootply.com editor -->\n\t<script type=\'text/javascript\'>\n\t$(document).ready(function() {\n\t});\n\t</script>\n\t\n\t<!-- Jasney-->\n\t<script src="jasny-bootstrap/js/jasny-bootstrap.min.js"></script>\n\n    </body>\n\n</html>'
    >>> listArticleId = getListArticleInTimeInterval(doctestDbInfo, 1399664864 - 1 * 24 * 3600, 1399664864, 1)
    >>> print listArticleId
    [38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49]
    >>> getListArticlePage(doctestDbInfo, listArticleId, 1, displayType = 'email')
    u'\n<!DOCTYPE html>\n<html lang="en">\n    <head>\n        <meta http-equiv="content-type" content="text/html; charset=UTF-8"> \n        <title>Scooply</title>\n        <meta name="generator" content="Bootply" />\n        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">\t\t\n    </head>\n    \n\t<body>\n\t\n\t<h2>\n\t\tScooply /skoop-li/\n\t</h2>\n\t<p> Hello Zhi, </p>\n\t<p> This week\'s top-notch bioscience papers are ready to view. Enjoy!!</p>\n\t<p>Your Scooply team</p>\n\n\n\t\t<div class="outline">\n\t\t\t<h3>\n\t\t\t\tWhat\'s New\n\t\t\t</h3>\n\t\t\t<p>\n\t\t\t\tNow you can pin your favorite articles and view them <a href="http://www.scooply.info/listPinnedArticle?subscriberId=1">here</a>.\n\t\t\t</p>\n\n\t\t\t<h3>\n\t\t\t\tSummary\n\t\t\t</h3>\n\t\t\t\t\t\n\t\t\t<h4>\n\t\t\t\t<ul>\n\t\t\t\t\t<li><a href="#Science">Science (10 new)</a></li>\n\t\t\t\t\t<li><a href="#DNA sequencing">DNA sequencing (2 new)</a></li>\n\t\t\t\t</ul>\n\t\t\t</h4>\t\t\n\t\t</div>\n\t\t\t\t\t\t\n\t\t<div class="content_main">\n\t\t\n\n\t\n\t\t\t<h3>\n\t\t\t\tScience<a name="Science"></a>\n\t\t\t</h3>\n\t\t\t\t\t\n\t\n\t\t\t\t<div class="article_info">\n\t\t\t\t\t<h4> \n\t\t\t\t\t\t<a href="http://www.scooply.info/articleMore?subscriberId=1&amp;articleId=38" target="_blank">Structural basis for protein antiaggregation activity of the trigger factor chaperone.</a> <br>\n\t\t\t\t\t\tSaio et al., Kalodimos Lab <br>\n\t\t\t\t\t\t4 days ago in <span class="label label-default">Science</span> <br>\n\t\t\t\t\t</h4>\n\t\t\t\t</div>\n\t\n\t\t\t\t<div class="article_info">\n\t\t\t\t\t<h4> \n\t\t\t\t\t\t<a href="http://www.scooply.info/articleMore?subscriberId=1&amp;articleId=39" target="_blank">Sound strategies for hearing restoration.</a> <br>\n\t\t\t\t\t\tG\xe9l\xe9oc et al., Holt Lab <br>\n\t\t\t\t\t\t4 days ago in <span class="label label-default">Science</span> <br>\n\t\t\t\t\t</h4>\n\t\t\t\t</div>\n\t\n\t\t\t\t<div class="article_info">\n\t\t\t\t\t<h4> \n\t\t\t\t\t\t<a href="http://www.scooply.info/articleMore?subscriberId=1&amp;articleId=40" target="_blank">Gibberellin acts positively then negatively to control onset of flower formation in Arabidopsis.</a> <br>\n\t\t\t\t\t\tYamaguchi et al., Wagner Lab <br>\n\t\t\t\t\t\t4 days ago in <span class="label label-default">Science</span> <br>\n\t\t\t\t\t</h4>\n\t\t\t\t</div>\n\t\n\t\t\t\t<div class="article_info">\n\t\t\t\t\t<h4> \n\t\t\t\t\t\t<a href="http://www.scooply.info/articleMore?subscriberId=1&amp;articleId=41" target="_blank">Spatially distributed local fields in the hippocampus encode rat position.</a> <br>\n\t\t\t\t\t\tAgarwal et al., Sommer Lab <br>\n\t\t\t\t\t\t4 days ago in <span class="label label-default">Science</span> <br>\n\t\t\t\t\t</h4>\n\t\t\t\t</div>\n\t\n\t\t\t\t<div class="article_info">\n\t\t\t\t\t<h4> \n\t\t\t\t\t\t<a href="http://www.scooply.info/articleMore?subscriberId=1&amp;articleId=42" target="_blank">Restoration of large damage volumes in polymers.</a> <br>\n\t\t\t\t\t\tWhite et al., Gergely Lab <br>\n\t\t\t\t\t\t4 days ago in <span class="label label-default">Science</span> <br>\n\t\t\t\t\t</h4>\n\t\t\t\t</div>\n\t\n\t\t\t\t<div class="article_info">\n\t\t\t\t\t<h4> \n\t\t\t\t\t\t<a href="http://www.scooply.info/articleMore?subscriberId=1&amp;articleId=43" target="_blank">Hippocampal neurogenesis regulates forgetting during adulthood and infancy.</a> <br>\n\t\t\t\t\t\tAkers et al., Frankland Lab <br>\n\t\t\t\t\t\t4 days ago in <span class="label label-default">Science</span> <br>\n\t\t\t\t\t</h4>\n\t\t\t\t</div>\n\t\n\t\t\t\t<div class="article_info">\n\t\t\t\t\t<h4> \n\t\t\t\t\t\t<a href="http://www.scooply.info/articleMore?subscriberId=1&amp;articleId=44" target="_blank">Vascular and neurogenic rejuvenation of the aging mouse brain by young systemic factors.</a> <br>\n\t\t\t\t\t\tKatsimpardi et al., Rubin Lab <br>\n\t\t\t\t\t\t4 days ago in <span class="label label-default">Science</span> <br>\n\t\t\t\t\t</h4>\n\t\t\t\t</div>\n\t\n\t\t\t\t<div class="article_info">\n\t\t\t\t\t<h4> \n\t\t\t\t\t\t<a href="http://www.scooply.info/articleMore?subscriberId=1&amp;articleId=45" target="_blank">Restoring systemic GDF11 levels reverses age-related dysfunction in mouse skeletal muscle.</a> <br>\n\t\t\t\t\t\tSinha et al., Wagers Lab <br>\n\t\t\t\t\t\t4 days ago in <span class="label label-default">Science</span> <br>\n\t\t\t\t\t</h4>\n\t\t\t\t</div>\n\t\n\t\t\t\t<div class="article_info">\n\t\t\t\t\t<h4> \n\t\t\t\t\t\t<a href="http://www.scooply.info/articleMore?subscriberId=1&amp;articleId=46" target="_blank">Identification of LRRC8 heteromers as an essential component of the volume-regulated anion channel VRAC.</a> <br>\n\t\t\t\t\t\tVoss et al., Jentsch Lab <br>\n\t\t\t\t\t\t4 days ago in <span class="label label-default">Science</span> <br>\n\t\t\t\t\t</h4>\n\t\t\t\t</div>\n\t\n\t\t\t\t<div class="article_info">\n\t\t\t\t\t<h4> \n\t\t\t\t\t\t<a href="http://www.scooply.info/articleMore?subscriberId=1&amp;articleId=47" target="_blank">The transcription factor Gata6 links tissue macrophage phenotype and proliferative renewal.</a> <br>\n\t\t\t\t\t\tRosas et al., Taylor Lab <br>\n\t\t\t\t\t\t4 days ago in <span class="label label-default">Science</span> <br>\n\t\t\t\t\t</h4>\n\t\t\t\t</div>\n\n\n\t\n\t\t\t<h3>\n\t\t\t\tDNA sequencing<a name="DNA sequencing"></a>\n\t\t\t</h3>\n\t\t\t\t\t\n\t\n\t\t\t\t<div class="article_info">\n\t\t\t\t\t<h4> \n\t\t\t\t\t\t<a href="http://www.scooply.info/articleMore?subscriberId=1&amp;articleId=48" target="_blank">Paternal poly (adp-ribose) metabolism modulates retention of inheritable sperm histones and early embryonic gene expression.</a> <br>\n\t\t\t\t\t\tIhara et al., Meyer Lab <br>\n\t\t\t\t\t\t4 days ago in <span class="label label-default">PLoS Genet.</span> <br>\n\t\t\t\t\t\tAlert on <span class="label label-default">DNA sequencing</span>\n\t\t\t\t\t</h4>\n\t\t\t\t</div>\n\t\n\t\t\t\t<div class="article_info">\n\t\t\t\t\t<h4> \n\t\t\t\t\t\t<a href="http://www.scooply.info/articleMore?subscriberId=1&amp;articleId=49" target="_blank">Genome Sequencing and Comparative Genomics of the Broad Host-Range Pathogen Rhizoctonia solani AG8.</a> <br>\n\t\t\t\t\t\tHane et al., Singh Lab <br>\n\t\t\t\t\t\t4 days ago in <span class="label label-default">PLoS Genet.</span> <br>\n\t\t\t\t\t\tAlert on <span class="label label-default">DNA sequencing</span>\n\t\t\t\t\t</h4>\n\t\t\t\t</div>\n\n\t\t<h3>\n\t\t\tFeedback\n\t\t</h3>\n\n\t\t<p> We are persistently working towards improving our search quality. \n\t\tIf the displayed results do not match your expectation, or if you have any\n\t\tsuggestions, we would greatly appreciate your feedback by replying to this \n\t\temail.\n\t\t\t\n\t\t</div><!-- content_main-->\n\n    </body>\n\n</html>'
    >>> recordSubscriberArticle(doctestDbInfo, 1, 7, '', Subscriber_ArticleEventCategory.pinned, dbBoolean.yes)
    >>> phdb = PhDatabase(MysqlConnection(doctestDbInfo['dbName'],doctestDbInfo['ip'],doctestDbInfo['user'],doctestDbInfo['password']))
    >>> phdb.fetchall('SELECT category, status FROM subscriber_articleEvent JOIN subscriber_article ON subscriber_articleEvent.subscriber_articleId = subscriber_article.subscriber_articleId WHERE articleId = 7 ORDER BY timestamp DESC')
    (0, ((2, 1), (1, 1), (1, 1)))
    >>> phdb.close()
    >>> getSubscriberEmail(doctestDbInfo, 1)
    u'lizhi1981@gmail.com'
    >>> import time
    >>> from phInfo import testEmailInfo
    >>> phdb = PhDatabase(MysqlConnection(doctestDbInfo['dbName'],doctestDbInfo['ip'],doctestDbInfo['user'],doctestDbInfo['password']))
    >>> phdb.getSubscriber_ArticleStatus(1, 7, Subscriber_ArticleEventCategory.created)
    1
    >>> phdb.getSubscriber_ArticleStatus(1, 7, Subscriber_ArticleEventCategory.pinned)
    1
    >>> phdb.getSubscriber_ArticleStatus(1, 7, Subscriber_ArticleEventCategory.moreClicked)
    0
    >>> phdb.getSubscriber_ArticleStatus(1, 7, Subscriber_ArticleEventCategory.extlinkClicked)
    0
    >>> phdb.close()
    >>> emailListArticleToSubscriber(doctestDbInfo, testEmailInfo, 1, sinceDaysAgo = 2, now = 1399664864)
    'Content-Type: multipart/alternative;\n boundary="===============3999968421347287993=="\nMIME-Version: 1.0\nSubject: This week\'s bioscience hot papers, brought to you by Scooply\nFrom: test@scooply.info\nTo: lizhi1981@gmail.com\n\n--===============3999968421347287993==\nContent-Type: text/plain; charset="us-ascii"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\n\nPlain text to be added.\n--===============3999968421347287993==\nContent-Type: text/html; charset="us-ascii"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 8bit\n\n\n<!DOCTYPE html>\n<html lang="en">\n    <head>\n        <meta http-equiv="content-type" content="text/html; charset=UTF-8"> \n        <title>Scooply</title>\n        <meta name="generator" content="Bootply" />\n        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">\t\t\n    </head>\n    \n\t<body>\n\t\n\t<h2>\n\t\tScooply /skoop-li/\n\t</h2>\n\t<p> Hello Zhi, </p>\n\t<p> This week\'s top-notch bioscience papers are ready to view. Enjoy!!</p>\n\t<p>Your Scooply team</p>\n\n\n\t\t<div class="outline">\n\t\t\t<h3>\n\t\t\t\tWhat\'s New\n\t\t\t</h3>\n\t\t\t<p>\n\t\t\t\tNow you can pin your favorite articles and view them <a href="http://www.scooply.info/listPinnedArticle?subscriberId=1">here</a>.\n\t\t\t</p>\n\n\t\t\t<h3>\n\t\t\t\tSummary\n\t\t\t</h3>\n\t\t\t\t\t\n\t\t\t<h4>\n\t\t\t\t<ul>\n\t\t\t\t\t<li><a href="#Nature">Nature (11 new)</a></li>\n\t\t\t\t\t<li><a href="#Science">Science (10 new)</a></li>\n\t\t\t\t\t<li><a href="#DNA sequencing">DNA sequencing (3 new)</a></li>\n\t\t\t\t</ul>\n\t\t\t</h4>\t\t\n\t\t</div>\n\t\t\t\t\t\t\n\t\t<div class="content_main">\n\t\t\n\n\t\n\t\t\t<h3>\n\t\t\t\tNature<a name="Nature"></a>\n\t\t\t</h3>\n\t\t\t\t\t\n\t\n\t\t\t\t<div class="article_info">\n\t\t\t\t\t<h4> \n\t\t\t\t\t\t<a href="http://www.scooply.info/articleMore?subscriberId=1&amp;articleId=24" target="_blank">Consequences of biodiversity loss for litter decomposition across biomes.</a> <br>\n\t\t\t\t\t\tHanda et al., H\xc3\xa4ttenschwiler Lab <br>\n\t\t\t\t\t\t5 days ago in <span class="label label-default">Nature</span> <br>\n\t\t\t\t\t</h4>\n\t\t\t\t</div>\n\t\n\t\t\t\t<div class="article_info">\n\t\t\t\t\t<h4> \n\t\t\t\t\t\t<a href="http://www.scooply.info/articleMore?subscriberId=1&amp;articleId=28" target="_blank">Niche filling slows the diversification of Himalayan songbirds.</a> <br>\n\t\t\t\t\t\tPrice et al., Mohan Lab <br>\n\t\t\t\t\t\t5 days ago in <span class="label label-default">Nature</span> <br>\n\t\t\t\t\t</h4>\n\t\t\t\t</div>\n\t\n\t\t\t\t<div class="article_info">\n\t\t\t\t\t<h4> \n\t\t\t\t\t\t<a href="http://www.scooply.info/articleMore?subscriberId=1&amp;articleId=29" target="_blank">Astrocyte-encoded positional cues maintain sensorimotor circuit integrity.</a> <br>\n\t\t\t\t\t\tMolofsky et al., Rowitch Lab <br>\n\t\t\t\t\t\t5 days ago in <span class="label label-default">Nature</span> <br>\n\t\t\t\t\t</h4>\n\t\t\t\t</div>\n\t\n\t\t\t\t<div class="article_info">\n\t\t\t\t\t<h4> \n\t\t\t\t\t\t<a href="http://www.scooply.info/articleMore?subscriberId=1&amp;articleId=30" target="_blank">Signal amplification and transduction in phytochrome photosensors.</a> <br>\n\t\t\t\t\t\tTakala et al., Westenhoff Lab <br>\n\t\t\t\t\t\t5 days ago in <span class="label label-default">Nature</span> <br>\n\t\t\t\t\t</h4>\n\t\t\t\t</div>\n\t\n\t\t\t\t<div class="article_info">\n\t\t\t\t\t<h4> \n\t\t\t\t\t\t<a href="http://www.scooply.info/articleMore?subscriberId=1&amp;articleId=31" target="_blank">Predicting biodiversity change and averting collapse in agricultural landscapes.</a> <br>\n\t\t\t\t\t\tMendenhall et al., Daily Lab <br>\n\t\t\t\t\t\t5 days ago in <span class="label label-default">Nature</span> <br>\n\t\t\t\t\t</h4>\n\t\t\t\t</div>\n\t\n\t\t\t\t<div class="article_info">\n\t\t\t\t\t<h4> \n\t\t\t\t\t\t<a href="http://www.scooply.info/articleMore?subscriberId=1&amp;articleId=32" target="_blank">Listeria monocytogenes exploits efferocytosis to promote cell-to-cell spread.</a> <br>\n\t\t\t\t\t\tCzuczman et al., Brumell Lab <br>\n\t\t\t\t\t\t5 days ago in <span class="label label-default">Nature</span> <br>\n\t\t\t\t\t</h4>\n\t\t\t\t</div>\n\t\n\t\t\t\t<div class="article_info">\n\t\t\t\t\t<h4> \n\t\t\t\t\t\t<a href="http://www.scooply.info/articleMore?subscriberId=1&amp;articleId=33" target="_blank">NRROS negatively regulates reactive oxygen species during host defence and autoimmunity.</a> <br>\n\t\t\t\t\t\tNoubade et al., Ouyang Lab <br>\n\t\t\t\t\t\t5 days ago in <span class="label label-default">Nature</span> <br>\n\t\t\t\t\t</h4>\n\t\t\t\t</div>\n\t\n\t\t\t\t<div class="article_info">\n\t\t\t\t\t<h4> \n\t\t\t\t\t\t<a href="http://www.scooply.info/articleMore?subscriberId=1&amp;articleId=34" target="_blank">Synapse elimination and learning rules co-regulated by MHC class I H2-Db.</a> <br>\n\t\t\t\t\t\tLee et al., Shatz Lab <br>\n\t\t\t\t\t\t5 days ago in <span class="label label-default">Nature</span> <br>\n\t\t\t\t\t</h4>\n\t\t\t\t</div>\n\t\n\t\t\t\t<div class="article_info">\n\t\t\t\t\t<h4> \n\t\t\t\t\t\t<a href="http://www.scooply.info/articleMore?subscriberId=1&amp;articleId=35" target="_blank">Endosomes are specialized platforms for bacterial sensing and NOD2 signalling.</a> <br>\n\t\t\t\t\t\tNakamura et al., Mellman Lab <br>\n\t\t\t\t\t\t5 days ago in <span class="label label-default">Nature</span> <br>\n\t\t\t\t\t</h4>\n\t\t\t\t</div>\n\t\n\t\t\t\t<div class="article_info">\n\t\t\t\t\t<h4> \n\t\t\t\t\t\t<a href="http://www.scooply.info/articleMore?subscriberId=1&amp;articleId=36" target="_blank">Sensory stimulation shifts visual cortex from synchronous to asynchronous states.</a> <br>\n\t\t\t\t\t\tTan et al., Priebe Lab <br>\n\t\t\t\t\t\t5 days ago in <span class="label label-default">Nature</span> <br>\n\t\t\t\t\t</h4>\n\t\t\t\t</div>\n\t\n\t\t\t\t<div class="article_info">\n\t\t\t\t\t<h4> \n\t\t\t\t\t\t<a href="http://www.scooply.info/articleMore?subscriberId=1&amp;articleId=37" target="_blank">FXR is a molecular target for the effects of vertical sleeve gastrectomy.</a> <br>\n\t\t\t\t\t\tRyan et al., Seeley Lab <br>\n\t\t\t\t\t\t5 days ago in <span class="label label-default">Nature</span> <br>\n\t\t\t\t\t</h4>\n\t\t\t\t</div>\n\n\n\t\n\t\t\t<h3>\n\t\t\t\tScience<a name="Science"></a>\n\t\t\t</h3>\n\t\t\t\t\t\n\t\n\t\t\t\t<div class="article_info">\n\t\t\t\t\t<h4> \n\t\t\t\t\t\t<a href="http://www.scooply.info/articleMore?subscriberId=1&amp;articleId=38" target="_blank">Structural basis for protein antiaggregation activity of the trigger factor chaperone.</a> <br>\n\t\t\t\t\t\tSaio et al., Kalodimos Lab <br>\n\t\t\t\t\t\t4 days ago in <span class="label label-default">Science</span> <br>\n\t\t\t\t\t</h4>\n\t\t\t\t</div>\n\t\n\t\t\t\t<div class="article_info">\n\t\t\t\t\t<h4> \n\t\t\t\t\t\t<a href="http://www.scooply.info/articleMore?subscriberId=1&amp;articleId=39" target="_blank">Sound strategies for hearing restoration.</a> <br>\n\t\t\t\t\t\tG\xc3\xa9l\xc3\xa9oc et al., Holt Lab <br>\n\t\t\t\t\t\t4 days ago in <span class="label label-default">Science</span> <br>\n\t\t\t\t\t</h4>\n\t\t\t\t</div>\n\t\n\t\t\t\t<div class="article_info">\n\t\t\t\t\t<h4> \n\t\t\t\t\t\t<a href="http://www.scooply.info/articleMore?subscriberId=1&amp;articleId=40" target="_blank">Gibberellin acts positively then negatively to control onset of flower formation in Arabidopsis.</a> <br>\n\t\t\t\t\t\tYamaguchi et al., Wagner Lab <br>\n\t\t\t\t\t\t4 days ago in <span class="label label-default">Science</span> <br>\n\t\t\t\t\t</h4>\n\t\t\t\t</div>\n\t\n\t\t\t\t<div class="article_info">\n\t\t\t\t\t<h4> \n\t\t\t\t\t\t<a href="http://www.scooply.info/articleMore?subscriberId=1&amp;articleId=41" target="_blank">Spatially distributed local fields in the hippocampus encode rat position.</a> <br>\n\t\t\t\t\t\tAgarwal et al., Sommer Lab <br>\n\t\t\t\t\t\t4 days ago in <span class="label label-default">Science</span> <br>\n\t\t\t\t\t</h4>\n\t\t\t\t</div>\n\t\n\t\t\t\t<div class="article_info">\n\t\t\t\t\t<h4> \n\t\t\t\t\t\t<a href="http://www.scooply.info/articleMore?subscriberId=1&amp;articleId=42" target="_blank">Restoration of large damage volumes in polymers.</a> <br>\n\t\t\t\t\t\tWhite et al., Gergely Lab <br>\n\t\t\t\t\t\t4 days ago in <span class="label label-default">Science</span> <br>\n\t\t\t\t\t</h4>\n\t\t\t\t</div>\n\t\n\t\t\t\t<div class="article_info">\n\t\t\t\t\t<h4> \n\t\t\t\t\t\t<a href="http://www.scooply.info/articleMore?subscriberId=1&amp;articleId=43" target="_blank">Hippocampal neurogenesis regulates forgetting during adulthood and infancy.</a> <br>\n\t\t\t\t\t\tAkers et al., Frankland Lab <br>\n\t\t\t\t\t\t4 days ago in <span class="label label-default">Science</span> <br>\n\t\t\t\t\t</h4>\n\t\t\t\t</div>\n\t\n\t\t\t\t<div class="article_info">\n\t\t\t\t\t<h4> \n\t\t\t\t\t\t<a href="http://www.scooply.info/articleMore?subscriberId=1&amp;articleId=44" target="_blank">Vascular and neurogenic rejuvenation of the aging mouse brain by young systemic factors.</a> <br>\n\t\t\t\t\t\tKatsimpardi et al., Rubin Lab <br>\n\t\t\t\t\t\t4 days ago in <span class="label label-default">Science</span> <br>\n\t\t\t\t\t</h4>\n\t\t\t\t</div>\n\t\n\t\t\t\t<div class="article_info">\n\t\t\t\t\t<h4> \n\t\t\t\t\t\t<a href="http://www.scooply.info/articleMore?subscriberId=1&amp;articleId=45" target="_blank">Restoring systemic GDF11 levels reverses age-related dysfunction in mouse skeletal muscle.</a> <br>\n\t\t\t\t\t\tSinha et al., Wagers Lab <br>\n\t\t\t\t\t\t4 days ago in <span class="label label-default">Science</span> <br>\n\t\t\t\t\t</h4>\n\t\t\t\t</div>\n\t\n\t\t\t\t<div class="article_info">\n\t\t\t\t\t<h4> \n\t\t\t\t\t\t<a href="http://www.scooply.info/articleMore?subscriberId=1&amp;articleId=46" target="_blank">Identification of LRRC8 heteromers as an essential component of the volume-regulated anion channel VRAC.</a> <br>\n\t\t\t\t\t\tVoss et al., Jentsch Lab <br>\n\t\t\t\t\t\t4 days ago in <span class="label label-default">Science</span> <br>\n\t\t\t\t\t</h4>\n\t\t\t\t</div>\n\t\n\t\t\t\t<div class="article_info">\n\t\t\t\t\t<h4> \n\t\t\t\t\t\t<a href="http://www.scooply.info/articleMore?subscriberId=1&amp;articleId=47" target="_blank">The transcription factor Gata6 links tissue macrophage phenotype and proliferative renewal.</a> <br>\n\t\t\t\t\t\tRosas et al., Taylor Lab <br>\n\t\t\t\t\t\t4 days ago in <span class="label label-default">Science</span> <br>\n\t\t\t\t\t</h4>\n\t\t\t\t</div>\n\n\n\t\n\t\t\t<h3>\n\t\t\t\tDNA sequencing<a name="DNA sequencing"></a>\n\t\t\t</h3>\n\t\t\t\t\t\n\t\n\t\t\t\t<div class="article_info">\n\t\t\t\t\t<h4> \n\t\t\t\t\t\t<a href="http://www.scooply.info/articleMore?subscriberId=1&amp;articleId=48" target="_blank">Paternal poly (adp-ribose) metabolism modulates retention of inheritable sperm histones and early embryonic gene expression.</a> <br>\n\t\t\t\t\t\tIhara et al., Meyer Lab <br>\n\t\t\t\t\t\t4 days ago in <span class="label label-default">PLoS Genet.</span> <br>\n\t\t\t\t\t\tAlert on <span class="label label-default">DNA sequencing</span>\n\t\t\t\t\t</h4>\n\t\t\t\t</div>\n\t\n\t\t\t\t<div class="article_info">\n\t\t\t\t\t<h4> \n\t\t\t\t\t\t<a href="http://www.scooply.info/articleMore?subscriberId=1&amp;articleId=49" target="_blank">Genome Sequencing and Comparative Genomics of the Broad Host-Range Pathogen Rhizoctonia solani AG8.</a> <br>\n\t\t\t\t\t\tHane et al., Singh Lab <br>\n\t\t\t\t\t\t4 days ago in <span class="label label-default">PLoS Genet.</span> <br>\n\t\t\t\t\t\tAlert on <span class="label label-default">DNA sequencing</span>\n\t\t\t\t\t</h4>\n\t\t\t\t</div>\n\t\n\t\t\t\t<div class="article_info">\n\t\t\t\t\t<h4> \n\t\t\t\t\t\t<a href="http://www.scooply.info/articleMore?subscriberId=1&amp;articleId=51" target="_blank">Simultaneous assessment of the macrobiome and microbiome in a bulk sample of tropical arthropods through DNA metasystematics.</a> <br>\n\t\t\t\t\t\tGibson et al., Hajibabaei Lab <br>\n\t\t\t\t\t\t5 days ago in <span class="label label-default">Proc. Natl. Acad. Sci. U.S.A.</span> <br>\n\t\t\t\t\t\tAlert on <span class="label label-default">DNA sequencing</span>\n\t\t\t\t\t</h4>\n\t\t\t\t</div>\n\n\t\t<h3>\n\t\t\tFeedback\n\t\t</h3>\n\n\t\t<p> We are persistently working towards improving our search quality. \n\t\tIf the displayed results do not match your expectation, or if you have any\n\t\tsuggestions, we would greatly appreciate your feedback by replying to this \n\t\temail.\n\t\t\t\n\t\t</div><!-- content_main-->\n\n    </body>\n\n</html>\n--===============3999968421347287993==--'
    >>> verifyPasswordAndGetSubscriberId(doctestDbInfo, 'henrylee18@yahoo.com', '123')
    (True, 2L)
    >>> verifyPasswordAndGetSubscriberId(doctestDbInfo, 'henrylee17@yahoo.com', '123')
    (False, None)
    
    '''
 
    timeStr = createPubmedTimeStr(queryStartTime, queryEndTime)

    'connect pubhub database'
    phdb = PhDatabase(MysqlConnection(dbInfo['dbName'],dbInfo['ip'],dbInfo['user'],dbInfo['password']))    
    
    res = createPubmedQueryList(phdb, subscriberIdIn)
    
    for queryStr, listSubscriber, queryPhrase in res:
        
        'add time constraint'
        queryStr += ' AND '+ timeStr
        
        'add type: journal article'
        #queryStr += ' AND (Journal Article[ptyp])'

        info('query: '+queryStr)
        info('subscribers: '+str(listSubscriber))   
            
        'URL encoding'
        queryStr = urllib2.quote(queryStr.encode("ascii"))
        
        debug('query: \n\n'+queryStr+'\n')
        
        'query pubmed'
        pa = PubmedApi()
        ldArticle, ldAuthor = pa.query(queryStr, 100)
        
        for dArticle in ldArticle:
                                       
            'record article'
            dArticle['articleId'] = None #prepare to get LAST_INSERT_ID
            
            try:
                articleId = phdb.insertOneReturnLastInsertId('article', dArticle) 
            except MySQLdb.IntegrityError:
                'key duplication. already in database. try to select'
                _, articleId = phdb.selectDistinct('article',['articleId',],
                                                'PMID = '+dArticle['PMID'])                
                articleId = singleStrip(articleId)[0]
                
            if articleId == -1: #article insertion fails (could be already in db)
                continue
            
            for s in listSubscriber:
                                                                   
                'record subscriber_article'
                dSubscriber_article = {}
                dSubscriber_article['subscriber_articleId'] = None
                dSubscriber_article['subscriberId'] = s
                dSubscriber_article['articleId'] = articleId
                dSubscriber_article['queryPhrase'] = queryPhrase 
                                            # journal name or keyword or author
                
                try:
                    subscriber_articleId = phdb.insertOneReturnLastInsertId(
                                        'subscriber_article', dSubscriber_article)
                except MySQLdb.IntegrityError:
                    continue
                
                'record subscriber_articleEvent'
                dSubscriber_articleEvent = {}
                dSubscriber_articleEvent['subscriber_articleId'] = subscriber_articleId
                dSubscriber_articleEvent['timestamp'] = createMysqlDatetimeStr(time.time())
                dSubscriber_articleEvent['category'] = Subscriber_ArticleEventCategory.created
                dSubscriber_articleEvent['status'] = dbBoolean.yes

                try:
                    phdb.insertOne('subscriber_articleEvent', dSubscriber_articleEvent)
                except MySQLdb.IntegrityError:
                    continue

        'record author'
        #ldAuthorForArticle = [l for l in ldAuthor if l['PMID']==dArticle['PMID']]
        replaceKeyValuePair(phdb, ldAuthor, 'article', 'PMID', 'articleId')
                                # Need to look up articleId in article, 
                                # and replace key PMID with articleID
        try:
            phdb.insertMany('author', ldAuthor)
        except MySQLdb.IntegrityError:
            pass
        
    '''lastly, if the operation for all subscribers instead of any individual
    subscriber, also update the record in phDatabaseUpdateEvent'''
    if subscriberIdIn is None:
        d = {}
        now = time.time()
        d['timestamp'] = createMysqlDatetimeStr(now)
        phdb.insertOne('phDatabaseUpdateEvent',d)    
        
    'close pubhub database'
    phdb.close()
    
def getListArticleInTimeInterval(dbInfo, startTime, endTime, subscriberId):
    '''
    Note: startTime and endTime are both in epoch (unix) time.
    '''
    startTime = createMysqlDatetimeStr(startTime)
    endTime = createMysqlDatetimeStr(endTime)
    phdb = PhDatabase(MysqlConnection(dbInfo['dbName'],dbInfo['ip'],
                                      dbInfo['user'],dbInfo['password']))
    queryStartTime=time.time()

    s = u'''SELECT DISTINCT article.articleId
    FROM article 
    JOIN subscriber_article ON article.articleId = subscriber_article.articleId 
    WHERE subscriber_article.subscriberId = %s 
    AND article.DateCreated > '%s' 
    AND article.DateCreated < '%s'
    ;''' % (subscriberId, startTime, endTime)
    
    _, listArticleId = phdb.fetchall(s)
    
    timeElapsed = time.time()-queryStartTime
    if timeElapsed > 0.1:
        warning("getListArticleInTimeInterval 2 tables join takes %.2f sec!" % timeElapsed)
    
    phdb.close()

    if listArticleId is None:
        listArticleId = []
    else:        
        listArticleId = singleStrip(listArticleId)
        #ORDER BY article.DateCreated DESC
        
        #FIXME ad hoc, revise
        listArticleId = map(lambda x: int(x), listArticleId)
        
    return listArticleId

def getListArticlePage(dbInfo, listArticleId, subscriberId, displayType = 'regular'):
    
    phdb = PhDatabase(MysqlConnection(dbInfo['dbName'],dbInfo['ip'],
                                      dbInfo['user'],dbInfo['password']))
    
    'FIXME: 4 tables join!'
    queryStartTime=time.time()

    'old method:'
#     _, res = phdb.fetchall(u'''SELECT DISTINCT article.articleId, ArticleTitle, 
#     JournalISOAbbreviation, DateCreated, firstAuthor.authorId, firstAuthor.initials, 
#     firstAuthor.lastName, firstAuthor.affiliation, lastAuthor.authorId, 
#     lastAuthor.lastName, lastAuthor.affiliation, DoiId, PMID, subscriber_article.queryPhrase
#     FROM article 
#     JOIN subscriber_article ON article.articleId = subscriber_article.articleId 
#     JOIN firstAuthor ON article.articleId = firstAuthor.articleId 
#     JOIN lastAuthor ON article.articleId = lastAuthor.articleId 
#     WHERE subscriber_article.subscriberId = %s 
#     AND article.DateCreated > '%s' 
#     AND article.DateCreated < '%s'
#     ;''' % (subscriberId, startTime, endTime))
    
    'new method:'
    
    if len(listArticleId) == 0:
        res = []
    else:
        if len(listArticleId) == 1:
            ls = '(' + str(listArticleId[0]) + ')'
        else:
            ls = str(tuple(listArticleId))
        s = u'''SELECT DISTINCT article.articleId, ArticleTitle, 
        JournalISOAbbreviation, DateCreated, firstAuthor.authorId, firstAuthor.initials, 
        firstAuthor.lastName, firstAuthor.affiliation, lastAuthor.authorId, 
        lastAuthor.lastName, lastAuthor.affiliation, DoiId, PMID, subscriber_article.queryPhrase
        FROM article 
        JOIN subscriber_article ON article.articleId = subscriber_article.articleId 
        JOIN firstAuthor ON article.articleId = firstAuthor.articleId 
        JOIN lastAuthor ON article.articleId = lastAuthor.articleId 
        WHERE subscriber_article.subscriberId = %s 
        AND article.articleId IN %s
        ORDER BY FIELD(article.articleId, %s
        ;''' % (str(subscriberId), ls, ls[1:])
        
        '''
        Note above is similar to:
        SELECT * FROM table WHERE id IN (118,17,113,23,72) 
        ORDER BY FIELD(id,118,17,113,23,72)
        '''
        
        _, res = phdb.fetchall(s)
     
    timeElapsed = time.time()-queryStartTime
    if timeElapsed > 0.1:
        warning("getListArticlePage 4 tables join takes %.2f sec!" % timeElapsed)
    
    _, res2 = phdb.selectDistinct('subscriber', ['firstName', 'lastName', 'email'], 
                                 'subscriberId = ' + str(subscriberId))
    firstName, lastName, email = res2[0]

    phdb.close()
    
    rows=[]
    for (articleId, ArticleTitle, JournalTitle, DateCreated, firstAuthorId, 
    firstAuthorInitials, firstAuthorLastName, firstAuthorAffiliation, 
    lastAuthorId, lastAuthorLastName, lastAuthorAffiliation, DoiId, PMID, 
    queryPhrase) in res:
    
        dayStr = createDayStr(DateCreated)
        
        affiliation=''
        if firstAuthorAffiliation != '':
            affiliation = firstAuthorAffiliation
        elif lastAuthorAffiliation != '':
            affiliation = lastAuthorAffiliation

#         if DoiId != '':
#             www = 'http://dx.doi.org/' + DoiId
#         else: 
#             www = 'http://www.ncbi.nlm.nih.gov/pubmed/' + str(PMID)
#         www = urllib2.quote(www.encode("ascii"))
            
        if displayType == 'email':
            
#             articleLinkStr = 'http://'+webServerInfo['addr']+ '/' \
#                         'redirect?subscriberId=%s&articleId=%s&redirectUrl=%s' \
#                         % (subscriberId,str(articleId),www)

            'now all link to our website:'
            articleLinkStr = 'http://'+webServerInfo['addr']+ '/' \
                        'articleMore?subscriberId=%s&articleId=%s' \
                        % (subscriberId,str(articleId))
                        
        else:
            articleLinkStr = 'articleMore?subscriberId=%s&articleId=%s' \
                        % (subscriberId,str(articleId))
                    
        if firstAuthorLastName and firstAuthorLastName != '':
            if firstAuthorId != lastAuthorId:
                authorField = firstAuthorLastName+' et al., '+lastAuthorLastName+' Lab'
            else:
                authorField = ''
                if firstAuthorInitials and firstAuthorInitials != '':
                    authorField += firstAuthorInitials+' '
                authorField += firstAuthorLastName
        else:
            authorField = ''
            
        rows.append((queryPhrase, ArticleTitle, JournalTitle, dayStr, authorField, 
                     affiliation, articleLinkStr))
        
    name = ''
    if firstName:
        name = firstName
    elif lastName:
        name = lastName
    elif email:
        name = email
    else:
        name = 'stranger'
        
    listPinnedArticleStr = 'http://'+webServerInfo['addr']+ '/' \
                        'listPinnedArticle?subscriberId=%s' \
                        % subscriberId
    
    args = (name,listPinnedArticleStr)
                
    if displayType == 'email':
        output = template('views/emailListArticle', rows = rows, args = args)
    elif displayType == 'pinned':
        output = template('views/listPinnedArticle', rows = rows)
    else: # 'regular'
        output = template('views/listArticle', rows = rows)
    
    return output

def getArticleMorePage(dbInfo, subscriberId, articleId):
    
    phdb = PhDatabase(MysqlConnection(dbInfo['dbName'],dbInfo['ip'],
                                      dbInfo['user'],dbInfo['password']))

    _, resArticle = phdb.fetchall(u'''SELECT DISTINCT article.articleId, ArticleTitle, 
    Abstract, JournalISOAbbreviation, DateCreated, DoiId, PMID, 
    subscriber_article.queryPhrase
    FROM article 
    JOIN subscriber_article ON article.articleId = subscriber_article.articleId 
    WHERE subscriber_article.subscriberId = %s 
    AND article.articleId = %s
    ;''' % (str(subscriberId), str(articleId)))
    resArticle = resArticle[0]
         
    (articleId, ArticleTitle, Abstract, JournalTitle, DateCreated, DoiId, PMID, 
    queryPhrase) = resArticle
    
    _, resAuthor = phdb.selectDistinct('author', ['Initials', 'LastName', 
            'Affiliation', 'AuthorOrder',], u'articleId = %s' % articleId)
    
    'get if article has been pinned'
    pinned = phdb.getSubscriber_ArticleStatus(subscriberId, articleId, 
                                Subscriber_ArticleEventCategory.pinned)
    
    phdb.close()
        
    dayStr = createDayStr(DateCreated)

    '''resAuthor one row: col 0 - Initials, col 1 - LastName, 
                          col 2 - Affiliation, col 3 - AuthorOrder'''

    listAuthorOrder = map(lambda x: x[3], resAuthor)
    orderFirstAuthor = min(listAuthorOrder)
    orderLastAuthor = max(listAuthorOrder)
    firstAuthor = [a for a in resAuthor if a[3] == orderFirstAuthor][0]
    lastAuthor = [a for a in resAuthor if a[3] == orderLastAuthor][0]
    firstAuthorAffiliation = firstAuthor[2]
    lastAuthorAffiliation = lastAuthor[2]
    affiliation = ''
    if firstAuthorAffiliation != '':
        affiliation = firstAuthorAffiliation
    elif lastAuthorAffiliation != '':
        affiliation = lastAuthorAffiliation
    
    listFirstLastAuthorName = map(lambda x: (x[0], x[1]), resAuthor)
    authorStr = createAuthorStr(listFirstLastAuthorName)
    
    if DoiId != '':
        wwwDoiId = 'http://dx.doi.org/' + DoiId
        wwwDoiId = urllib2.quote(wwwDoiId.encode("ascii"))
        DoiIdLinkStr = 'redirect?subscriberId=%s&articleId=%s&redirectUrl=%s' \
                            % (subscriberId,str(articleId),wwwDoiId)
    else:
        DoiIdLinkStr = ''

    if PMID != '':
        wwwPMID = 'http://www.ncbi.nlm.nih.gov/pubmed/' + str(PMID)    
        wwwPMID = urllib2.quote(wwwPMID.encode("ascii"))
        PMIDLinkStr = 'redirect?subscriberId=%s&articleId=%s&redirectUrl=%s' \
                            % (subscriberId,str(articleId),wwwPMID)
    else:
        PMIDLinkStr = ''
            
    if pinned == dbBoolean.no:
        pinStr = 'Pin'
        toPin = dbBoolean.yes
    else:
        pinStr = 'Unpin'
        toPin = dbBoolean.no
        
    pinLinkStr = 'pin?subscriberId=%s&articleId=%s&status=%s' \
                % (subscriberId, str(articleId), toPin)
                
    listLinkStr = 'listArticle?subscriberId=%s' % subscriberId
    
    args = (ArticleTitle, Abstract, JournalTitle, queryPhrase, dayStr, 
            authorStr, affiliation, DoiIdLinkStr, PMIDLinkStr, pinLinkStr, 
            pinStr, listLinkStr)
    
    output = template('views/articleMore', args = args)
    
    return output



def recordSubscriberArticle(dbInfo, subscriberId, articleId, extraInfo, category, status):
    
    phdb = PhDatabase(MysqlConnection(dbInfo['dbName'],dbInfo['ip'],
                                      dbInfo['user'],dbInfo['password']))
    'record'
    _, s_aId = phdb.selectDistinct('subscriber_article',['subscriber_articleId'],
                                 'subscriberId = %s AND articleId = %s' %
                                 (str(subscriberId), str(articleId)))
    #FIXME: what if s_aId is None
    s_aId = singleStrip(s_aId)[0] # need double strip
    
    s_aEventDict={}
    s_aEventDict['subscriber_articleId'] = s_aId
    s_aEventDict['timestamp'] = createMysqlDatetimeStr(time.time())
    s_aEventDict['category'] = category
    s_aEventDict['status'] = status
    s_aEventDict['extraInfo'] = extraInfo
    phdb.insertOne('subscriber_articleEvent',s_aEventDict)

    phdb.close()
    
def signUpSubscriber(dbInfo, email, password, firstName, lastName, areaId, keywords):
    'Return: subscriberId'

    phdb = PhDatabase(MysqlConnection(dbInfo['dbName'],dbInfo['ip'],
                                      dbInfo['user'],dbInfo['password']))
    
    '====insert subscriber===='
    s={}
    s['subscriberId'] = None # prepare for return
    s['firstName'] = firstName
    s['lastName'] = lastName
    s['email'] = email
    s['password'] = password
    try:
        subscriberId = phdb.insertOneReturnLastInsertId('subscriber',s)
    except MySQLdb.IntegrityError:
        subscriberId = -2 #FIXME: very ad hoc subscriberId is +ve if successful
        
    '====insert interest===='
    if subscriberId > 0: #subscriber inserted without error
        si=[]
        _, areaName = phdb.selectDistinct('area',['areaName'],'areaId = ' 
                                                                + str(areaId))
        areaName = singleStrip(areaName)[0] #double strip
        '==area=='
        a={}
        a['subscriberId'] = subscriberId
        a['category'] = str(InterestCategory.area)
        a['phrase'] = areaName
        si.append(a)
        '==generalJournl=='
        _, listGeneralJournalTitle = phdb.fetchall('''
        SELECT DISTINCT journal.journalTitle FROM journal
        JOIN journal_area ON journal.journalId = journal_area.journalId
        WHERE journal_area.areaId = %s AND journal.isGeneral = 1
        ''' % str(areaId))
        listGeneralJournalTitle = singleStrip(listGeneralJournalTitle)
        for journalTitle in listGeneralJournalTitle:
            j={}
            j['subscriberId'] = subscriberId
            j['category'] = str(InterestCategory.generalJournal) 
            j['phrase'] = journalTitle
            si.append(j)
        '==expertJournal=='
        _, listExpertJournalTitle = phdb.fetchall('''
        SELECT DISTINCT journal.journalTitle FROM journal
        JOIN journal_area ON journal.journalId = journal_area.journalId
        WHERE journal_area.areaId = %s AND journal.isGeneral = 0
        ''' % str(areaId))
        listExpertJournalTitle = singleStrip(listExpertJournalTitle)
        for journalTitle in listExpertJournalTitle:
            j={}
            j['subscriberId'] = subscriberId
            j['category'] = str(InterestCategory.expertJournal)
            j['phrase'] = journalTitle
            si.append(j)
        '==keyword=='
        for keyword in keywords:
            k={}
            k['subscriberId'] = subscriberId
            k['category'] = str(InterestCategory.keyword)
            k['phrase'] = keyword
            si.append(k)
    
        phdb.insertMany('interest',si)
         
    phdb.close()
    
    return subscriberId

def getSubscriberEmail(dbInfo, subscriberId):
    'Return email address'

    'look up subscriber email address'
    phdb = PhDatabase(MysqlConnection(dbInfo['dbName'],dbInfo['ip'],
                                      dbInfo['user'],dbInfo['password']))
    _, email = phdb.selectDistinct('subscriber', ['email'], 
                                      'subscriberId = '+str(subscriberId))
    email = singleStrip(email)[0]
    
    phdb.close()
    
    return email

def getLastPhDatabaseUpdateTime(dbInfo):
    'Return last Pubhub database time.'
    phdb = PhDatabase(MysqlConnection(dbInfo['dbName'],dbInfo['ip'],
                                      dbInfo['user'],dbInfo['password']))
    _, lastTime = phdb.fetchall('''SELECT UNIX_TIMESTAMP(timestamp) 
                                   FROM phDatabaseUpdateEvent
                                   ORDER BY timestamp DESC LIMIT 1''')
    if not lastTime:
        lastTime = None # No records
    else:
        lastTime = singleStrip(lastTime)[0]

    phdb.close()

    return lastTime

def emailListArticleToSubscriber(dbInfo, emailInfo, subscriberId, sinceDaysAgo = 7, now = None):
    
    sender = emailInfo['mainEmail']

    receiver = getSubscriberEmail(dbInfo, subscriberId)
    
    'Create message container - the correct MIME type is multipart/alternative'
    msg = MIMEMultipart('alternative')
    msg['Subject'] = '''This week's bioscience hot papers, brought to you by Scooply'''
    msg['From'] = sender
    msg['To'] = receiver
    
    'create message body'
    text = 'Plain text to be added.'

    if now is None:
        now = time.time()
    startTime = now - sinceDaysAgo * 24 * 3600
    endTime = now
    
    listArticleId = getListArticleInTimeInterval(dbInfo, startTime, endTime, subscriberId)
    html = getListArticlePage(dbInfo, listArticleId, subscriberId, displayType = 'email')

    'record the MIME types of both parts - text/plain and text/html'
    part1 = MIMEText(text.encode('utf8'), 'plain')
    part2 = MIMEText(html.encode('utf8'), 'html')
    
    '''
    Attach parts into message container.
    According to RFC 2046, the last part of a multipart message, in this case
    the HTML message, is best and preferred.
    '''
    msg.attach(part1)
    msg.attach(part2)
    msg = msg.as_string()
    
    'open server'
    emailServer = smtplib.SMTP(emailInfo['server'], emailInfo['port'])
    emailServer.starttls()
    emailServer.login(emailInfo['user'], emailInfo['password'])

    'send email'
    emailServer.sendmail(sender, [receiver], msg)
    
    'close server'
    emailServer.quit()
    
    return msg

def getListPinnedArticle(dbInfo, subscriberId):
    
    phdb = PhDatabase(MysqlConnection(dbInfo['dbName'],dbInfo['ip'],
                                      dbInfo['user'],dbInfo['password']))
    queryStartTime=time.time()

    'FIXME: three layers join!'
    _, listArticleId = phdb.fetchall(u'''
    SELECT articleId FROM subscriber_article 
    JOIN pinnedSubscriber_ArticleStatus 
    ON pinnedSubscriber_ArticleStatus.subscriber_articleId 
    = subscriber_article.subscriber_articleId 
    WHERE subscriberId = %s and status = %s
    ORDER BY pinnedSubscriber_ArticleStatus.timestamp DESC
    ''' % (subscriberId, str(dbBoolean.yes)))
    
    listArticleId = singleStrip(listArticleId)
    
    #FIXME ad hoc, revise
    listArticleId = map(lambda x: int(x), listArticleId)
    
    timeElapsed = time.time()-queryStartTime
    if timeElapsed > 0.1:
        warning("getListPinnedArticle takes %.2f sec!" % timeElapsed)
    
    phdb.close()
    
    return listArticleId

def verifyPasswordAndGetSubscriberId(dbInfo, email, password):
    phdb = PhDatabase(MysqlConnection(dbInfo['dbName'],dbInfo['ip'],
                                      dbInfo['user'],dbInfo['password']))

    _, res = phdb.selectDistinct('subscriber', ['subscriberId',], 
                      "email = '%s' AND password = '%s'" % (email, password))

    phdb.close()

    if not res:
        ret = (False, None)
    else:
        res = singleStrip(res)[0]
        ret = (True, res)
    
    return ret
    
if __name__ == '__main__':

    import doctest
    print doctest.testmod()
         

    
    
    
    
    