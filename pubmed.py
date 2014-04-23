#!/usr/bin/python
'''
Sandbox for testing Pubmed API

Created on April 10, 2014

@author: leeoz

@email: lizhi1981@gmail.com

'''

import sys
import httplib2
import xml.etree.ElementTree as et
import MySQLdb
# from lxml import etree
import myTools
import time

def testPubmed():
    '''
    return: 0 if exit normally; otherwise 1.
    '''
    
    print 'download pubmed records in pubmed that match query...'    
    
    '  tmp'
    base='http://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
    db='pubmed'
    retmax=100
    retstart=1

#     query='Science[Journal]+AND+(2005/07/01[PDAT]+:+2010/07/12[PDAT])'
#     query='Cell[Journal]+AND+(2008/07/01[PDAT]+:+2010/07/12[PDAT])'
    query='Nature[Journal]+AND+(2009/07/01[PDAT]+:+2009/07/12[PDAT])'
#     query='Molecular+Cell[Journal]+AND+(2010/05/01[PDAT]+:+2010/07/12[PDAT])'
#     query='Molecular+and+cellular+biology[Journal]+AND+(2010/05/01[PDAT]+:+2011/07/12[PDAT])'
    
    print '  query pubmed...'
    searchUrl=base+'esearch.fcgi?'+'db='+db+'&term='+query+'&retmax=' \
                    +str(retmax)+'&retstart='+str(retstart) \
                    +'&email=pubhub2@gmail.com' 
    #Note: httplib2 is the plain-vanilla version. If encounter problems 
    #use urllib2 instead.
    print '    GET '+searchUrl+' ...'
    try:
        _,searchContent=httplib2.Http().request(searchUrl,"GET")
    except Exception as e:
        print e
        return 1
    else:
        print '    return:\n\n'+searchContent
    
    print '  parse returned article ID...'
    #FIXME: do DTD check for returned xml file
    '''
    xml MUST be in format of: <eSearchResult>(root)
                                 <IdList>?
                                     <Id>*
    '''
    try:
        searchRoot=et.fromstring(searchContent)
        n=searchRoot
        c=myTools.findAllAndAssert(n,'IdList','?')
        if len(c)==0:
            raise myTools.MyException("cannot parse IdList.")
            
        n=c[0]
        c=myTools.findAllAndAssert(n,'Id','*')
        if not c: #empyty list, no article found
            raise myTools.MyException("no article found.")

        listId=[n.text for n in c]
        print '    returned ID: '+str(listId)
    except myTools.MyException as e:
        print e
        return 0
    except Exception as e:
        print e   
        return 1            

    print '  retrieve article details...'
    fetchUrl=base+'efetch.fcgi?'+'db='+db+'&id='
    for i in listId:
        fetchUrl+=(i+',')
    fetchUrl+='&retmode=xml'
    
    print '    GET '+fetchUrl+' ...'
    try:
        _,fetchContent=httplib2.Http().request(fetchUrl,"GET")
    except Exception as e:
        print e
        return 1
    else:
        pass
#         print '    return:\n\n'+fetchContent
            
    print '  parse article details...'
    #FIXME: do DTD check for returned xml file
    '''
    xml is in format of: <PubmedArticleSet>(root)
                             <PubmedArticle>+
                                 <MedlineCitation>
                                     <PMID>
                                     <DateCreated>
                                     <DateCompleted>?
                                     <Article>
                                         <Journal>
                                             <ISSN>
                                             <JournalIssue>
                                                 <Volume>
                                                 <Issue>
                                                 <PubDate>
                                             <Title>
                                             <ISOAbbreviation>
                                         <ArticleTitle>
                                         <ELocationID>
                                         <Abstract>
                                         <AuthorList>
                                             <Author>+
                                                 <LastName>
                                                 <ForeName>
                                                 <Initials>
                                                 <Affiliation>?
                                         <Language>
                                         <PublicationTypeList>
                                             <PublicationType>*
                                 <PubmedData>
                                     <History>
                                         <PubMedPubDate>*  (received,accepted,...)
                                     <ArticleIdList>* (pii,doi,pubmed,...)
    For now, need to extract minimal pieces of info and store in DB:
    PMID,DateCreated,JournalVolume,JournalIssue,PubDate,JournalTitle,JournalISOAbbreviation,
    ArticleTitle,DoiId,Abstract,ListAuthorLastName,ListAuthorForeName,
    ListAuthorInitials,ListAuthorAffiliation,FirstAuthor,LastAuthor
                                     
    '''

    try:
        #dbAddr="ec2-54-193-189-136.us-west-1.compute.amazonaws.com"
        #db=MySQLdb.connect(dbAddr,"root","abc1234","pubhub")        
        dbAddr="ec2-54-187-100-110.us-west-2.compute.amazonaws.com"
        db=MySQLdb.connect(dbAddr,"root","lymanDelmedio123","pubhub")

    except Exception as e:
        print e
        db.close()
        return 1
    
    fetchRoot=et.fromstring(fetchContent)
    nPubmedArticleSet=fetchRoot
    cPubmedArticle=myTools.findAllAndAssert(nPubmedArticleSet, 'PubmedArticle', '+')
    nArticleTotal=0
    nArticleSuccess=0
    nAuthorTotal=0
    nAuthorSuccess=0
    for i,nPubmedArticle in enumerate(cPubmedArticle):

        print '    article %d:' % (i+1)
        
        parseStartTime=time.time()

        PMID=''
        DateCreated=''
        JournalVolume=''
        JournalIssue=''
        PubDate=''
        JournalTitle=''
        JournalISOAbbreviation=''
        ArticleTitle=''
        DoiId=''
        Abstract=''
        ListAuthorForeName=[]
        ListAuthorInitials=[]
        ListAuthorLastName=[]
        ListAuthorAffiliation=[]
        
        'notation convention: c for children, n for node'
        
        cMedlineCitation=myTools.findAllAndAssert(nPubmedArticle,'MedlineCitation','?')
        if len(cMedlineCitation)==1:
            nMedlineCitation=cMedlineCitation[0]
                    
            cPMID=myTools.findAllAndAssert(nMedlineCitation,'PMID','?')
            if len(cPMID)==1:
                nPMID=cPMID[0]
                PMID+=nPMID.text
            
            cDateCreated=myTools.findAllAndAssert(nMedlineCitation,'DateCreated','?')
            if len(cDateCreated)==1:
                nDateCreated=cDateCreated[0]
                
                cYear=myTools.findAllAndAssert(nDateCreated,'Year','?')
                if len(cYear)==1:
                    nYear=cYear[0]
                    DateCreated+=nYear.text
                            
                cMonth=myTools.findAllAndAssert(nDateCreated,'Month','?')
                if len(cMonth)==1:
                    nMonth=cMonth[0]
                    DateCreated+='-'+nMonth.text

                cDay=myTools.findAllAndAssert(nDateCreated,'Day','?')
                if len(cDay)==1:
                    nDay=cDay[0]
                    DateCreated+='-'+nDay.text
                                
            cArticle=myTools.findAllAndAssert(nMedlineCitation,'Article','?')
            if len(cArticle)==1:
                nArticle=cArticle[0]
                
                cJournal=myTools.findAllAndAssert(nArticle,'Journal','?')
                if len(cJournal)==1:
                    nJournal=cJournal[0]
                    
                    cJournalIssue=myTools.findAllAndAssert(nJournal,'JournalIssue','?')
                    if len(cJournalIssue)==1:
                        nJournalIssue=cJournalIssue[0]
                        
                        cVolume=myTools.findAllAndAssert(nJournalIssue,'Volume','?')
                        if len(cVolume)==1:
                            nVolume=cVolume[0]
                            JournalVolume+=nVolume.text
                            
                        cIssue=myTools.findAllAndAssert(nJournalIssue,'Issue','?')
                        if len(cIssue)==1:
                            nIssue=cIssue[0]
                            JournalIssue+=nIssue.text

                        cPubDate=myTools.findAllAndAssert(nJournalIssue,'PubDate','?')
                        if len(cPubDate)==1:
                            nPubDate=cPubDate[0]

                            cYear=myTools.findAllAndAssert(nPubDate,'Year','?')
                            if len(cYear)==1:
                                nYear=cYear[0]
                                PubDate+=nYear.text
                                        
                            cMonth=myTools.findAllAndAssert(nPubDate,'Month','?')
                            if len(cMonth)==1:
                                nMonth=cMonth[0]
                                PubDate+='-'+nMonth.text
            
                            cDay=myTools.findAllAndAssert(nPubDate,'Day','?')
                            if len(cDay)==1:
                                nDay=cDay[0]
                                PubDate+='-'+nDay.text
                    
                    cTitle=myTools.findAllAndAssert(nJournal,'Title','?')
                    if len(cTitle)==1:
                        nTitle=cTitle[0]
                        JournalTitle+=nTitle.text

                    cISOAbbreviation=myTools.findAllAndAssert(nJournal,'ISOAbbreviation','?')
                    if len(cISOAbbreviation)==1:
                        nISOAbbreviation=cISOAbbreviation[0]
                        JournalISOAbbreviation+=nISOAbbreviation.text
        
                cArticleTitle=myTools.findAllAndAssert(nArticle,'ArticleTitle','?')
                if len(cArticleTitle)==1:
                    nArticleTitle=cArticleTitle[0]
                    ArticleTitle+=nArticleTitle.text
                
                cELocationID=myTools.findAllAndAssert(nArticle,'ELocationID','?')
                if len(cELocationID)==1:
                    nELocationID=cELocationID[0]
                    aElocationID=nELocationID.attrib
                    if ('EIdType' in aElocationID) and \
                        ('ValidYN' in aElocationID) and \
                        aElocationID['EIdType']=='doi' and \
                        aElocationID['ValidYN']=='Y':
                        DoiId+=nELocationID.text
        
                cAbstract=myTools.findAllAndAssert(nArticle,'Abstract','?')
                if len(cAbstract)==1:
                    nAbstract=cAbstract[0]
                    
                    cAbstractText=myTools.findAllAndAssert(nAbstract,'AbstractText','?')
                    if len(cAbstractText)==1:
                        nAbstractText=cAbstractText[0]
                        Abstract+=nAbstractText.text
                    
                cAuthorList=myTools.findAllAndAssert(nArticle,'AuthorList','?')
                if len(cAuthorList)==1:
                    nAuthorList=cAuthorList[0]
                    
                    cAuthor=myTools.findAllAndAssert(nAuthorList,'Author','+')
                    for snAuthor,nAuthor in enumerate(cAuthor):
                        try:                        
                            cForeName=myTools.findAllAndAssert(nAuthor,'ForeName','?')                        
                            if len(cForeName)==1:
                                nForeName=cForeName[0]
                                foreNameText=nForeName.text.encode(sys.stdout.encoding, errors='replace').replace("\"","'")
                                ListAuthorForeName.append(foreNameText)
                            else:
                                ListAuthorForeName.append("")
    
                            cInitials=myTools.findAllAndAssert(nAuthor,'Initials','?')                        
                            if len(cInitials)==1:
                                nInitials=cInitials[0]
                                initialsText=nInitials.text.encode(sys.stdout.encoding, errors='replace').replace("\"","'")
                                ListAuthorInitials.append(initialsText)
                            else:
                                ListAuthorInitials.append("")
                                                        
                            cLastName=myTools.findAllAndAssert(nAuthor,'LastName','?')                        
                            if len(cLastName)==1:
                                nLastName=cLastName[0]
                                lastNameText=nLastName.text.encode(sys.stdout.encoding, errors='replace').replace("\"","'")
                                ListAuthorLastName.append(lastNameText)
                            else:
                                ListAuthorLastName.append("")
                    
                            cAffiliation=myTools.findAllAndAssert(nAuthor,'Affiliation','?')                        
                            if len(cAffiliation)==1:
                                nAffiliation=cAffiliation[0]
                                affiliationText=nAffiliation.text.encode(sys.stdout.encoding, errors='replace').replace("\"","'")
                                ListAuthorAffiliation.append(affiliationText)
                            else:
                                ListAuthorAffiliation.append("")
                        except Exception as e:
                            print e
                            continue
        try:
            JournalTitle=JournalTitle.encode(sys.stdout.encoding, errors='replace').replace("\"","'")
            JournalISOAbbreviation=JournalISOAbbreviation.encode(sys.stdout.encoding, errors='replace').replace("\"","'")
            ArticleTitle=ArticleTitle.encode(sys.stdout.encoding, errors='replace').replace("\"","'")
            Abstract=Abstract.encode(sys.stdout.encoding, errors='replace').replace("\"","'")
            PubDate=myTools.myNormalizedDate(PubDate)
        except Exception as e:
            print e
            continue
        
        print '      PMID: '+PMID
        print '      DateCreated: '+DateCreated
        print '      JournalVolume: '+JournalVolume
        print '      JournalIssue: '+JournalIssue
        print '      PubDate: '+PubDate
        print '      JournalTitle: '+JournalTitle
        print '      JournalISOAbbreviation: '+JournalISOAbbreviation
        print '      ArticleTitle: '+ArticleTitle
        print '      DoiId: '+DoiId
        print '      Abstract: '+Abstract
        print '      ListAuthorForeName: '+str(ListAuthorForeName)
        print '      ListAuthorInitials: '+str(ListAuthorInitials)
        print '      ListAuthorLastName: '+str(ListAuthorLastName)
        print '      ListAuthorAffiliation: '+str(ListAuthorAffiliation)

        print '      (parsing time: %f sec.)' % (time.time()-parseStartTime)
        
        print '\n      insert article details to database...'

        '''
        table schema:
                CREATE TABLE article(
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
                
                CREATE TABLE author(
                authorId INT NOT NULL AUTO_INCREMENT,
                articleId INT NOT NULL,
                ForeName VARCHAR(255),
                Initials VARCHAR(255),
                LastName VARCHAR(255),
                Affiliation TEXT,
                PRIMARY KEY (authorId),
                FOREIGN KEY (articleId) REFERENCES article(articleId)
                );
                // determine if an author is first: for articleId, authorId smallest; last: authorId largest
                // must make sure inserting is in order of first to last
        '''
                    
        #cursor.execute("SELECT VERSION()")
        #data=cursor.fetchone()
        #print "Database version : %s " % data
 
        sql="""insert into article
                (PMID,DateCreated,JournalVolume,JournalIssue,PubDate,
                JournalTitle,JournalISOAbbreviation,ArticleTitle,DoiId,Abstract) 
                VALUES (%d,"%s","%s","%s","%s","%s","%s","%s","%s","%s");
            """ % (int(PMID),DateCreated,JournalVolume,JournalIssue,PubDate,
                 JournalTitle,JournalISOAbbreviation,ArticleTitle,DoiId,Abstract)
             
#         print sql
             
        nArticleTotal+=1
        
        commitStartTime=time.time()
        try:
            cursor=db.cursor()    
            cursor.execute(sql)
            db.commit()
        except MySQLdb.Error as e:
            print "        article table commit failed. rollback."        
            db.rollback()
            print e
        except Exception as e:
            print e
            return 1
        else:
            print "        article table commit succeeded."
            nArticleSuccess+=1
            
        '    get articleId'
        sql="""select articleId from article where PMID=%d
            """ % int(PMID)
        try:
            cursor=db.cursor()
            cursor.execute(sql)
            results=cursor.fetchall()
            if len(results)==0:
                raise myTools.MyException("cannot retrieve article just inserted.")
            elif len(results)>1:
                raise myTools.MyException("should have one article with given PMID.")
        except Exception as e:
            print e
        else:
            articleId=results[0][0]
            
        nAuthorTotal+=1
        try:
            cursor=db.cursor()    
            for foreName,initials,lastName,affiliation in zip(ListAuthorForeName,
                    ListAuthorInitials,ListAuthorLastName,ListAuthorAffiliation):
                
                sql="""insert into author
                    (articleId,ForeName,Initials,LastName,Affiliation) 
                    VALUES (%d,"%s","%s","%s","%s");""" \
                    % (articleId,foreName,initials,lastName,affiliation)
    
                cursor.execute(sql)
            db.commit()
        except MySQLdb.Error as e:
            print "        author table commit failed. rollback."        
            db.rollback()
            print e
        except Exception as e:
            print e
            return 1
        else:
            print "        author table commit succeeded."
            nAuthorSuccess+=1
            
        print '      (committing time: %f sec.)' % (time.time()-commitStartTime)
        
            
    print '  %d of %d articles committed successfully.' % (nArticleSuccess,nArticleTotal)
    print '  %d of %d authors committed successfully.' % (nAuthorSuccess,nAuthorTotal)
            
    try:            
        db.close()
    except Exception as e:
        print e
        return 1
            
    return 0

if __name__ == '__main__':
    
    testPubmed()

    print 'Done.'
    
