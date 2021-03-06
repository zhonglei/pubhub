'''
Classes and methods for accessing the Pubmed database.

Created on Apr 25, 2014

@author: zhil2
'''

import time
import httplib2
import xml.etree.ElementTree as et
from logging import debug, warning
import pprint

import phTools

'''
format '%(asctime)s %(name)s %(levelname)s: %(message)s'
level DEBUG, INFO
'''
# import logging
# logging.basicConfig(format='%(name)s %(levelname)s: %(message)s',
#                     level=logging.DEBUG)

class PubmedApi(object):
    r'''
    Example:
    >>> pa = PubmedApi()
    >>> queryStr = 'Nature[Journal]+AND+(2012/07/01[PDAT]+:+2012/07/12[PDAT])'
    >>> l = pa.getMatchedPmid(queryStr,2)
    >>> print l
    ['22792548', '22785319']
    >>> pa.getArticleAndAuthorDetails(l)
    ([{'JournalVolume': '487', 'PubDate': '2012-7-12', 'JournalTitle': 'Nature', 'Abstract': u"The last deglaciation (21 to 7 thousand years ago) was punctuated by several abrupt meltwater pulses, which sometimes caused noticeable climate change. Around 14 thousand years ago, meltwater pulse 1A (MWP-1A), the largest of these events, produced a sea level rise of 14-18\u2009metres over 350\u2009years. Although this enormous surge of water certainly originated from retreating ice sheets, there is no consensus on the geographical source or underlying physical mechanisms governing the rapid sea level rise. Here we present an ice-sheet modelling simulation in which the separation of the Laurentide and Cordilleran ice sheets in North America produces a meltwater pulse corresponding to MWP-1A. Another meltwater pulse is produced when the Labrador and Baffin ice domes around Hudson Bay separate, which could be associated with the '8,200-year' event, the most pronounced abrupt climate event of the past nine thousand years. For both modelled pulses, the saddle between the two ice domes becomes subject to surface melting because of a general surface lowering caused by climate warming. The melting then rapidly accelerates as the saddle between the two domes gets lower, producing nine metres of sea level rise over 500 years. This mechanism of an ice 'saddle collapse' probably explains MWP-1A and the 8,200-year event and sheds light on the consequences of these events on climate.", 'JournalISOAbbreviation': 'Nature', 'DateCreated': '2012-07-12', 'ArticleTitle': 'Deglacial rapid sea level rises caused by ice-sheet saddle collapses.', 'PMID': '22785319', 'DoiId': '10.1038/nature11257', 'JournalIssue': '7406'}], [{'LastName': 'Gregoire', 'Affiliation': 'School of Geographical Sciences, University of Bristol, University Road, Bristol BS8 1SS, UK. lauren.gregoire@bristol.ac.uk', 'AuthorOrderReversed': 3, 'ForeName': 'Lauren J', 'PMID': '22785319', 'AuthorOrder': 1, 'Initials': 'LJ'}, {'LastName': 'Payne', 'Affiliation': '', 'AuthorOrderReversed': 2, 'ForeName': 'Antony J', 'PMID': '22785319', 'AuthorOrder': 2, 'Initials': 'AJ'}, {'LastName': 'Valdes', 'Affiliation': '', 'AuthorOrderReversed': 1, 'ForeName': 'Paul J', 'PMID': '22785319', 'AuthorOrder': 3, 'Initials': 'PJ'}])
    >>> pa.query(queryStr,3)
    ([{'JournalVolume': '487', 'PubDate': '2012-7-12', 'JournalTitle': 'Nature', 'Abstract': u"The last deglaciation (21 to 7 thousand years ago) was punctuated by several abrupt meltwater pulses, which sometimes caused noticeable climate change. Around 14 thousand years ago, meltwater pulse 1A (MWP-1A), the largest of these events, produced a sea level rise of 14-18\u2009metres over 350\u2009years. Although this enormous surge of water certainly originated from retreating ice sheets, there is no consensus on the geographical source or underlying physical mechanisms governing the rapid sea level rise. Here we present an ice-sheet modelling simulation in which the separation of the Laurentide and Cordilleran ice sheets in North America produces a meltwater pulse corresponding to MWP-1A. Another meltwater pulse is produced when the Labrador and Baffin ice domes around Hudson Bay separate, which could be associated with the '8,200-year' event, the most pronounced abrupt climate event of the past nine thousand years. For both modelled pulses, the saddle between the two ice domes becomes subject to surface melting because of a general surface lowering caused by climate warming. The melting then rapidly accelerates as the saddle between the two domes gets lower, producing nine metres of sea level rise over 500 years. This mechanism of an ice 'saddle collapse' probably explains MWP-1A and the 8,200-year event and sheds light on the consequences of these events on climate.", 'JournalISOAbbreviation': 'Nature', 'DateCreated': '2012-07-12', 'ArticleTitle': 'Deglacial rapid sea level rises caused by ice-sheet saddle collapses.', 'PMID': '22785319', 'DoiId': '10.1038/nature11257', 'JournalIssue': '7406'}, {'JournalVolume': '487', 'PubDate': '2012-7-12', 'JournalTitle': 'Nature', 'Abstract': "Living organisms have unique homeostatic abilities, maintaining tight control of their local environment through interconversions of chemical and mechanical energy and self-regulating feedback loops organized hierarchically across many length scales. In contrast, most synthetic materials are incapable of continuous self-monitoring and self-regulating behaviour owing to their limited single-directional chemomechanical or mechanochemical modes. Applying the concept of homeostasis to the design of autonomous materials would have substantial impacts in areas ranging from medical implants that help stabilize bodily functions to 'smart' materials that regulate energy usage. Here we present a versatile strategy for creating self-regulating, self-powered, homeostatic materials capable of precisely tailored chemo-mechano-chemical feedback loops on the nano- or microscale. We design a bilayer system with hydrogel-supported, catalyst-bearing microstructures, which are separated from a reactant-containing 'nutrient' layer. Reconfiguration of the gel in response to a stimulus induces the reversible actuation of the microstructures into and out of the nutrient layer, and serves as a highly precise 'on/off' switch for chemical reactions. We apply this design to trigger organic, inorganic and biochemical reactions that undergo reversible, repeatable cycles synchronized with the motion of the microstructures and the driving external chemical stimulus. By exploiting a continuous feedback loop between various exothermic catalytic reactions in the nutrient layer and the mechanical action of the temperature-responsive gel, we then create exemplary autonomous, self-sustained homeostatic systems that maintain a user-defined parameter--temperature--in a narrow range. The experimental results are validated using computational modelling that qualitatively captures the essential features of the self-regulating behaviour and provides additional criteria for the optimization of the homeostatic function, subsequently confirmed experimentally. This design is highly customizable owing to the broad choice of chemistries, tunable mechanics and its physical simplicity, and may lead to a variety of applications in autonomous systems with chemo-mechano-chemical transduction at their core.", 'JournalISOAbbreviation': 'Nature', 'DateCreated': '2012-07-12', 'ArticleTitle': 'Synthetic homeostatic materials with chemo-mechano-chemical self-regulation.', 'PMID': '22785318', 'DoiId': '10.1038/nature11223', 'JournalIssue': '7406'}], [{'LastName': 'Gregoire', 'Affiliation': 'School of Geographical Sciences, University of Bristol, University Road, Bristol BS8 1SS, UK. lauren.gregoire@bristol.ac.uk', 'AuthorOrderReversed': 3, 'ForeName': 'Lauren J', 'PMID': '22785319', 'AuthorOrder': 1, 'Initials': 'LJ'}, {'LastName': 'Payne', 'Affiliation': '', 'AuthorOrderReversed': 2, 'ForeName': 'Antony J', 'PMID': '22785319', 'AuthorOrder': 2, 'Initials': 'AJ'}, {'LastName': 'Valdes', 'Affiliation': '', 'AuthorOrderReversed': 1, 'ForeName': 'Paul J', 'PMID': '22785319', 'AuthorOrder': 3, 'Initials': 'PJ'}, {'LastName': 'He', 'Affiliation': 'School of Engineering and Applied Sciences, Harvard University, Cambridge, Massachusetts 02138, USA.', 'AuthorOrderReversed': 7, 'ForeName': 'Ximin', 'PMID': '22785318', 'AuthorOrder': 1, 'Initials': 'X'}, {'LastName': 'Aizenberg', 'Affiliation': '', 'AuthorOrderReversed': 6, 'ForeName': 'Michael', 'PMID': '22785318', 'AuthorOrder': 2, 'Initials': 'M'}, {'LastName': 'Kuksenok', 'Affiliation': '', 'AuthorOrderReversed': 5, 'ForeName': 'Olga', 'PMID': '22785318', 'AuthorOrder': 3, 'Initials': 'O'}, {'LastName': 'Zarzar', 'Affiliation': '', 'AuthorOrderReversed': 4, 'ForeName': 'Lauren D', 'PMID': '22785318', 'AuthorOrder': 4, 'Initials': 'LD'}, {'LastName': 'Shastri', 'Affiliation': '', 'AuthorOrderReversed': 3, 'ForeName': 'Ankita', 'PMID': '22785318', 'AuthorOrder': 5, 'Initials': 'A'}, {'LastName': 'Balazs', 'Affiliation': '', 'AuthorOrderReversed': 2, 'ForeName': 'Anna C', 'PMID': '22785318', 'AuthorOrder': 6, 'Initials': 'AC'}, {'LastName': 'Aizenberg', 'Affiliation': '', 'AuthorOrderReversed': 1, 'ForeName': 'Joanna', 'PMID': '22785318', 'AuthorOrder': 7, 'Initials': 'J'}])
    >>> pa.getArticleAndAuthorDetails(['24805242',])
    ([{'JournalVolume': '509', 'PubDate': '2014-5-15', 'JournalTitle': 'Nature', 'Abstract': 'If and how the heart regenerates after an injury event is highly debated. c-kit-expressing cardiac progenitor cells have been reported as the primary source for generation of new myocardium after injury. Here we generated two genetic approaches in mice to examine whether endogenous c-kit(+) cells contribute differentiated cardiomyocytes to the heart during development, with ageing or after injury in adulthood. A complementary DNA encoding either Cre recombinase or a tamoxifen-inducible MerCreMer chimaeric protein was targeted to the Kit locus in mice and then bred with reporter lines to permanently mark cell lineage. Endogenous c-kit(+) cells did produce new cardiomyocytes within the heart, although at a percentage of approximately 0.03 or less, and if a preponderance towards cellular fusion is considered, the percentage falls to below approximately 0.008. By contrast, c-kit(+) cells amply generated cardiac endothelial cells. Thus, endogenous c-kit(+) cells can generate cardiomyocytes within the heart, although probably at a functionally insignificant level.', 'JournalISOAbbreviation': 'Nature', 'DateCreated': '2014-05-15', 'ArticleTitle': 'c-kit+ cells minimally contribute cardiomyocytes to the heart.', 'PMID': '24805242', 'DoiId': '10.1038/nature13309', 'JournalIssue': '7500'}], [{'LastName': 'van Berlo', 'Affiliation': "1] Department of Pediatrics, Cincinnati Children's Hospital Medical Center, Cincinnati, Ohio 45229, USA [2] Department of Medicine, division of Cardiology, Lillehei Heart Institute, University of Minnesota, Minneapolis, Minnesota 55455, USA [3].", 'AuthorOrderReversed': 9, 'ForeName': 'Jop H', 'PMID': '24805242', 'AuthorOrder': 1, 'Initials': 'JH'}, {'LastName': 'Kanisicak', 'Affiliation': "1] Department of Pediatrics, Cincinnati Children's Hospital Medical Center, Cincinnati, Ohio 45229, USA [2].", 'AuthorOrderReversed': 8, 'ForeName': 'Onur', 'PMID': '24805242', 'AuthorOrder': 2, 'Initials': 'O'}, {'LastName': 'Maillet', 'Affiliation': "Department of Pediatrics, Cincinnati Children's Hospital Medical Center, Cincinnati, Ohio 45229, USA.", 'AuthorOrderReversed': 7, 'ForeName': 'Marjorie', 'PMID': '24805242', 'AuthorOrder': 3, 'Initials': 'M'}, {'LastName': 'Vagnozzi', 'Affiliation': "Department of Pediatrics, Cincinnati Children's Hospital Medical Center, Cincinnati, Ohio 45229, USA.", 'AuthorOrderReversed': 6, 'ForeName': 'Ronald J', 'PMID': '24805242', 'AuthorOrder': 4, 'Initials': 'RJ'}, {'LastName': 'Karch', 'Affiliation': "Department of Pediatrics, Cincinnati Children's Hospital Medical Center, Cincinnati, Ohio 45229, USA.", 'AuthorOrderReversed': 5, 'ForeName': 'Jason', 'PMID': '24805242', 'AuthorOrder': 5, 'Initials': 'J'}, {'LastName': 'Lin', 'Affiliation': "Department of Pediatrics, Cincinnati Children's Hospital Medical Center, Cincinnati, Ohio 45229, USA.", 'AuthorOrderReversed': 4, 'ForeName': 'Suh-Chin J', 'PMID': '24805242', 'AuthorOrder': 6, 'Initials': 'SC'}, {'LastName': 'Middleton', 'Affiliation': 'Cedars-Sinai Heart Institute, 8700 Beverly Boulevard, Los Angeles, California 90048, USA.', 'AuthorOrderReversed': 3, 'ForeName': 'Ryan C', 'PMID': '24805242', 'AuthorOrder': 7, 'Initials': 'RC'}, {'LastName': u'Marb\xe1n', 'Affiliation': 'Cedars-Sinai Heart Institute, 8700 Beverly Boulevard, Los Angeles, California 90048, USA.', 'AuthorOrderReversed': 2, 'ForeName': 'Eduardo', 'PMID': '24805242', 'AuthorOrder': 8, 'Initials': 'E'}, {'LastName': 'Molkentin', 'Affiliation': "1] Department of Pediatrics, Cincinnati Children's Hospital Medical Center, Cincinnati, Ohio 45229, USA [2] Howard Hughes Medical Institute, Cincinnati Children's Hospital Medical Center, Cincinnati, Ohio 45229, USA.", 'AuthorOrderReversed': 1, 'ForeName': 'Jeffery D', 'PMID': '24805242', 'AuthorOrder': 9, 'Initials': 'JD'}])
    '''
    
    _base = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
    _db = 'pubmed'
    _email = 'pubhub2@gmail.com'
    _queryMinInterval = 0.5 #seconds. required not to query too frequently    
    
    def __init__(self):
        pass
    
    def getMatchedPmid(self, query, maxRes):
        '''
        Query database using starndard Pubmed query format.
        Return a list of PMIDs of matched articles with maximum length maxRes.
        '''
        debug('get PMID of articles matching query...')
        
        searchUrl=self._base+'esearch.fcgi?'+'db='+self._db+'&term='+query+'&retmax=' \
                        +str(maxRes)+'&email='+self._email 
        #Note: httplib2 is the plain-vanilla version. If encounter problems 
        #use urllib2 instead.
        debug('GET '+searchUrl+' ...')
        try:
            time.sleep(self._queryMinInterval)
            _,searchContent=httplib2.Http().request(searchUrl,"GET")
        except Exception as e:
            warning(e)
            return []
        else:
            debug('returned:\n\n'+searchContent)
         
        #FIXME: do DTD check for returned xml file
        '''
        xml MUST be in format of: <eSearchResult>(root)
                                     <IdList>?
                                         <Id>*
        '''
        try:
            searchRoot=et.fromstring(searchContent)
            n=searchRoot
            c=phTools.findAllAndAssert(n,'IdList','?')
            if len(c)==0:
                raise phTools.MyException("cannot parse IdList.")
                 
            n=c[0]
            c=phTools.findAllAndAssert(n,'Id','*')
            if not c: #empyty list, no article found
                raise phTools.MyException("no article found.")
     
            listId=[n.text for n in c]
            debug('returned ID: '+str(listId))
        except phTools.MyException as e:
            warning(e)
            return []
        except Exception as e:
            warning(e)   
            return []  
        
        return listId
    
    def getArticleAndAuthorDetails(self, listPmid):
        '''
        Query database with input of a list of PMIDs.
        Return a list of dictionaries of article details and a list of 
        dictionaries of author details.
        '''
        debug('get article and author details...')
        fetchUrl=self._base+'efetch.fcgi?'+'db='+self._db+'&id='
        for i in listPmid:
            fetchUrl+=(i+',')
        fetchUrl+='&retmode=xml'
        
        debug('GET '+fetchUrl+' ...')
        try:
            time.sleep(self._queryMinInterval)
            _,fetchContent=httplib2.Http().request(fetchUrl,"GET")
        except Exception as e:
            warning(e)
            return ([],[])
        else:
            debug('returned:\n\n'+fetchContent)

        res = self.parseArticleAndAuthor(fetchContent)
        
        return res
    
    def parseArticleAndAuthor(self,fetchContent):
        '''
        Parse article and author information from the returned fetchContent, 
        in XML format obeying the Pubmed efetch DTD format.
        '''
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
        
        listDictArticle=[]
        listDictAuthor=[]
        
        fetchRoot=et.fromstring(fetchContent)
        nPubmedArticleSet=fetchRoot
        cPubmedArticle=phTools.findAllAndAssert(nPubmedArticleSet, 'PubmedArticle', '+')
        for i,nPubmedArticle in enumerate(cPubmedArticle):
    
            debug('    article %d:' % (i+1))
            
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
            ListAuthorOrder=[]
            
            'notation convention: c for children, n for node'
            
            cMedlineCitation=phTools.findAllAndAssert(nPubmedArticle,'MedlineCitation','?')
            if len(cMedlineCitation)==1:
                nMedlineCitation=cMedlineCitation[0]
                        
                cPMID=phTools.findAllAndAssert(nMedlineCitation,'PMID','?')
                if len(cPMID)==1:
                    nPMID=cPMID[0]
                    PMID+=nPMID.text
                
                cDateCreated=phTools.findAllAndAssert(nMedlineCitation,'DateCreated','?')
                if len(cDateCreated)==1:
                    nDateCreated=cDateCreated[0]
                    
                    cYear=phTools.findAllAndAssert(nDateCreated,'Year','?')
                    if len(cYear)==1:
                        nYear=cYear[0]
                        DateCreated+=nYear.text
                                
                    cMonth=phTools.findAllAndAssert(nDateCreated,'Month','?')
                    if len(cMonth)==1:
                        nMonth=cMonth[0]
                        DateCreated+='-'+nMonth.text
    
                    cDay=phTools.findAllAndAssert(nDateCreated,'Day','?')
                    if len(cDay)==1:
                        nDay=cDay[0]
                        DateCreated+='-'+nDay.text
                                    
                cArticle=phTools.findAllAndAssert(nMedlineCitation,'Article','?')
                if len(cArticle)==1:
                    nArticle=cArticle[0]
                    
                    cJournal=phTools.findAllAndAssert(nArticle,'Journal','?')
                    if len(cJournal)==1:
                        nJournal=cJournal[0]
                        
                        cJournalIssue=phTools.findAllAndAssert(nJournal,'JournalIssue','?')
                        if len(cJournalIssue)==1:
                            nJournalIssue=cJournalIssue[0]
                            
                            cVolume=phTools.findAllAndAssert(nJournalIssue,'Volume','?')
                            if len(cVolume)==1:
                                nVolume=cVolume[0]
                                JournalVolume+=nVolume.text
                                
                            cIssue=phTools.findAllAndAssert(nJournalIssue,'Issue','?')
                            if len(cIssue)==1:
                                nIssue=cIssue[0]
                                JournalIssue+=nIssue.text
    
                            cPubDate=phTools.findAllAndAssert(nJournalIssue,'PubDate','?')
                            if len(cPubDate)==1:
                                nPubDate=cPubDate[0]
    
                                cYear=phTools.findAllAndAssert(nPubDate,'Year','?')
                                if len(cYear)==1:
                                    nYear=cYear[0]
                                    PubDate+=nYear.text
                                            
                                cMonth=phTools.findAllAndAssert(nPubDate,'Month','?')
                                if len(cMonth)==1:
                                    nMonth=cMonth[0]
                                    PubDate+='-'+nMonth.text
                
                                cDay=phTools.findAllAndAssert(nPubDate,'Day','?')
                                if len(cDay)==1:
                                    nDay=cDay[0]
                                    PubDate+='-'+nDay.text
                        
                        cTitle=phTools.findAllAndAssert(nJournal,'Title','?')
                        if len(cTitle)==1:
                            nTitle=cTitle[0]
                            JournalTitle+=nTitle.text
    
                        cISOAbbreviation=phTools.findAllAndAssert(nJournal,'ISOAbbreviation','?')
                        if len(cISOAbbreviation)==1:
                            nISOAbbreviation=cISOAbbreviation[0]
                            JournalISOAbbreviation+=nISOAbbreviation.text
            
                    cArticleTitle=phTools.findAllAndAssert(nArticle,'ArticleTitle','?')
                    if len(cArticleTitle)==1:
                        nArticleTitle=cArticleTitle[0]
                        ArticleTitle+=nArticleTitle.text
                    
                    cELocationID=phTools.findAllAndAssert(nArticle,'ELocationID','?')
                    if len(cELocationID)==1:
                        nELocationID=cELocationID[0]
                        aElocationID=nELocationID.attrib
                        #if ('EIdType' in aElocationID) and \
                        #    ('ValidYN' in aElocationID) and \
                        #    aElocationID['EIdType']=='doi' and \
                        #    aElocationID['ValidYN']=='Y':
                        if ('EIdType' in aElocationID) and \
                            aElocationID['EIdType']=='doi':\
                            DoiId+=nELocationID.text
            
                    cAbstract=phTools.findAllAndAssert(nArticle,'Abstract','?')
                    if len(cAbstract)==1:
                        nAbstract=cAbstract[0]
                        
                        cAbstractText=phTools.findAllAndAssert(nAbstract,'AbstractText','?')
                        if len(cAbstractText)==1:
                            nAbstractText=cAbstractText[0]
                            Abstract+=nAbstractText.text
                        
                    cAuthorList=phTools.findAllAndAssert(nArticle,'AuthorList','?')
                    if len(cAuthorList)==1:
                        nAuthorList=cAuthorList[0]
                        
                        cAuthor=phTools.findAllAndAssert(nAuthorList,'Author','+')
                        for snAuthor,nAuthor in enumerate(cAuthor):
                            try:  
                                
                                '''if author has CollectiveName, use last name field
                                to store it, and break'''
                                cCollectiveName=phTools.findAllAndAssert(nAuthor,'CollectiveName','?')                        
                                if len(cCollectiveName)==1:
                                    nCollectiveName=cCollectiveName[0]
                                    collectiveNameText=nCollectiveName.text
                                    ListAuthorLastName.append(collectiveNameText)
                                    ListAuthorForeName.append("")
                                    ListAuthorInitials.append("")
                                else:                                                      
                                    cForeName=phTools.findAllAndAssert(nAuthor,'ForeName','?')                        
                                    if len(cForeName)==1:
                                        nForeName=cForeName[0]
                                        foreNameText=nForeName.text
                                        ListAuthorForeName.append(foreNameText)
                                    else:
                                        ListAuthorForeName.append("")
            
                                    cInitials=phTools.findAllAndAssert(nAuthor,'Initials','?')                        
                                    if len(cInitials)==1:
                                        nInitials=cInitials[0]
                                        initialsText=nInitials.text
                                        ListAuthorInitials.append(initialsText)
                                    else:
                                        ListAuthorInitials.append("")
                                                                
                                    cLastName=phTools.findAllAndAssert(nAuthor,'LastName','?')                        
                                    if len(cLastName)==1:
                                        nLastName=cLastName[0]
                                        lastNameText=nLastName.text
                                        ListAuthorLastName.append(lastNameText)
                                    else:
                                        ListAuthorLastName.append("")
                        
                                cAffiliation=phTools.findAllAndAssert(nAuthor,'Affiliation','?')                        
                                if len(cAffiliation)==1:
                                    nAffiliation=cAffiliation[0]
                                    affiliationText=nAffiliation.text
                                    ListAuthorAffiliation.append(affiliationText)
                                else:
                                    ListAuthorAffiliation.append("")
                                    
                                ListAuthorOrder.append(snAuthor + 1)# order starts at 1
                                                                        
                            except Exception as e:
                                warning(e)
                                continue

            try:
                PubDate=phTools.myNormalizedDate(PubDate)
            except Exception as e:
                warning(e)
                continue
            
            'also store reversed author order -- to easily identify last author'
            ListAuthorOrderReversed = ListAuthorOrder[::-1]
            
            'Manual Filter rule: if no abstract'
            if Abstract == '':
                continue
            
            'Manual Filter rule: if no author, skip'
            if len(ListAuthorLastName) == 0:
                continue
                
            dictArticle={}
            dictArticle['PMID']=PMID
            dictArticle['DateCreated']=DateCreated
            dictArticle['JournalVolume']=JournalVolume
            dictArticle['JournalIssue']=JournalIssue
            dictArticle['PubDate']=PubDate
            dictArticle['JournalTitle']=JournalTitle
            dictArticle['JournalISOAbbreviation']=JournalISOAbbreviation
            dictArticle['ArticleTitle']=ArticleTitle
            dictArticle['DoiId']=DoiId
            dictArticle['Abstract']=Abstract

            listDictArticle.append(dictArticle)            

            for ForeName, Initials, LastName, Affiliation, AuthorOrder, AuthorOrderReversed \
                in zip(ListAuthorForeName, ListAuthorInitials, ListAuthorLastName, 
                ListAuthorAffiliation, ListAuthorOrder, ListAuthorOrderReversed):
                
                dictAuthor={}     
                dictAuthor['PMID']=PMID       
                dictAuthor['ForeName']=ForeName       
                dictAuthor['Initials']=Initials       
                dictAuthor['LastName']=LastName       
                dictAuthor['Affiliation']=Affiliation
                dictAuthor['AuthorOrder']=AuthorOrder
                dictAuthor['AuthorOrderReversed']=AuthorOrderReversed     

                listDictAuthor.append(dictAuthor)     
                
            debug('      (parsing time: %f sec.)' % (time.time()-parseStartTime))
                  
        debug('    listDictArticle:\n\n'+pprint.pformat(listDictArticle)+'\n')       
        debug('    listDictAuthor:\n\n'+pprint.pformat(listDictAuthor)+'\n')       
        
        return (listDictArticle,listDictAuthor)
    
    def query(self, query, maxRes):
        listPmid = self.getMatchedPmid(query, maxRes)
        if listPmid:
            res = self.getArticleAndAuthorDetails(listPmid)
        else:
            res = ([], [])
        return res

if __name__ == '__main__':
    import doctest
    print doctest.testmod()
