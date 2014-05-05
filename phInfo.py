'''
Administrative information.

Created on Apr 30, 2014

@author: zhil2
'''

webServerInfo = {'addr':'www.scooply.info',}

phDbInfo = {'dbName':'pubhub', 'ip':'54.187.112.65', 'user':'root', 
          'password':'lymanDelmedio123'}

testDbInfo = {'dbName':'testdb', 'ip':'54.187.112.65', 'user':'root', 
            'password':'lymanDelmedio123'}

emailInfo = {'server':'smtp.gmail.com', 'port':587, 'user':'pubhub2@gmail.com', 
           'password':'lymanDelmedio123', 'mainEmail':'scooply@scooply.info',
           }

class TestSubscriberInfo(object):
    
    @staticmethod
    def getLdSubscriber():
        ldSubscriber = [
                        {'firstName':'Franklin', 'lastName':'Zhong', 'email':'franklin.zhong@gmail.com'}, 
                        {'firstName':'Zhi', 'lastName':'Li', 'email':'lizhi1981@gmail.com'},
                        ]

        ld=ldSubscriber[:]
        return ld
    
    @staticmethod
    def getLdInterest():
        ldInterest = [
                        {'email':'franklin.zhong@gmail.com', 'category':'1', 'phrase':'biochemistry'}, 
                        {'email':'franklin.zhong@gmail.com', 'category':'1', 'phrase':'cell biology'}, 
                        {'email':'franklin.zhong@gmail.com', 'category':'2', 'phrase':'Nature'}, 
                        {'email':'franklin.zhong@gmail.com', 'category':'2', 'phrase':'Science'}, 
                        {'email':'franklin.zhong@gmail.com', 'category':'2', 'phrase':'Cell'}, 
                        {'email':'franklin.zhong@gmail.com', 'category':'3', 'phrase':'Molecular Cell'}, 
                        {'email':'franklin.zhong@gmail.com', 'category':'3', 'phrase':'Nature structural and Molecular Biology'}, 
                        {'email':'franklin.zhong@gmail.com', 'category':'3', 'phrase':'Molecular and Cellular Biology'}, 
                        {'email':'franklin.zhong@gmail.com', 'category':'4', 'phrase':'telomerase and cancer biology'}, 
                        {'email':'franklin.zhong@gmail.com', 'category':'4', 'phrase':'telomere and DNA replication'}, 
                          
                        {'email':'lizhi1981@gmail.com', 'category':'1', 'phrase':'biochemistry'}, 
                        {'email':'lizhi1981@gmail.com', 'category':'1', 'phrase':'Immunology'}, 
                        {'email':'lizhi1981@gmail.com', 'category':'2', 'phrase':'Cell'}, 
                        {'email':'lizhi1981@gmail.com', 'category':'2', 'phrase':'Science'}, 
                        {'email':'lizhi1981@gmail.com', 'category':'3', 'phrase':'Immunity'}, 
                        {'email':'lizhi1981@gmail.com', 'category':'3', 'phrase':'Journal of Immunology'}, 
                        {'email':'lizhi1981@gmail.com', 'category':'3', 'phrase':'Molecular Cell'}, 
                        {'email':'lizhi1981@gmail.com', 'category':'3', 'phrase':'Nature structural and Molecular Biology'}, 
                        {'email':'lizhi1981@gmail.com', 'category':'4', 'phrase':'noncoding RNA'}, 
      
                        ]# category: 1 - area, 2 - generalJournal, 3 - expertJournal, 4: keyword, 5 - author
        ld=ldInterest[:]
        return ld

class BiologyResearchInfo(object):
    
    @staticmethod
    def getListArea():
        l=[]
        l.append((1,'Bioinformatics and computational genomics'))
        l.append((2,'Biophysics and bioengineering'))
        l.append((3,'Developmental biology, stem cell biology and genetics'))
        l.append((4,'Microbiology and immunology'))
        l.append((5,'Biochemistry, cell biology and molecular biology'))
        l.append((6,'Neurosciences'))
        l.append((7,'Clinical sciences'))
        
        return l
    
    @staticmethod
    def getDictJournal_Area():
        dictJournal_Area={}
        dictJournal_Area['Nature'] = (1,2,3,4,5,6,7,)
        dictJournal_Area['Cell'] = (1,2,3,4,5,6,7,)
        dictJournal_Area['Science'] = (1,2,3,4,5,6,7,)
        dictJournal_Area['Nature Genetics'] = (1,2,3,4,5,6,7,)
        dictJournal_Area['? Current Biology'] = (1,2,3,4,5,6,)
        dictJournal_Area['? EMBO Journal'] = (1,2,3,4,5,6,7,)
        dictJournal_Area['? Proceedings of National Academy of Sciences'] = (1,2,3,4,5,6,7,)
        dictJournal_Area['Nature Biotechnology'] = (1,2,3,4,5,6,7,)
        dictJournal_Area['Nature Medicine'] = (1,2,3,4,5,6,7,)
        dictJournal_Area['Nature Methods'] = (1,2,3,4,5,6,)
        dictJournal_Area['Nature Structural & Molecular Biology'] = (1,2,3,4,5,6,7,)
        dictJournal_Area['Nature Cell Biology'] = (1,2,3,4,5,6,7,)
        dictJournal_Area['Nature Chemical Biology'] = (2,3,4,5,6,7,)
        dictJournal_Area['Molecular Cell'] = (1,2,3,4,5,6,7,)
        dictJournal_Area['Cancer Cell'] = (1,2,3,4,5,6,7,)
        dictJournal_Area['Cell Stem Cell'] = (1,2,3,4,5,6,7,)
        dictJournal_Area['Developmental Cell'] = (1,2,3,4,5,6,7,)
        dictJournal_Area['Cell Reports'] = (1,2,3,4,5,6,7,)
        dictJournal_Area['eLife'] = (1,2,3,4,5,6,7,)
        dictJournal_Area['Nature Communications'] = (1,2,3,4,5,6,7,)
        dictJournal_Area['Genes & Development'] = (1,2,3,4,5,6,7,)
        dictJournal_Area['Molecular and Cellular Biology'] = (1,2,3,4,5,6,7,)
        dictJournal_Area['Genome Biology'] = (1,)
        dictJournal_Area['Genome Research'] = (1,)
        dictJournal_Area['? Nucleic Acid Research'] = (1,2,5,)
        dictJournal_Area['Biophysical Journal'] = (2,)
        dictJournal_Area['Development'] = (3,)
        dictJournal_Area['PLoS Biology'] = (1,2,3,4,5,6,7,)
        dictJournal_Area['PLoS Medicine'] = (7,)
        dictJournal_Area['PLoS Genetics'] = (1,2,3,4,5,6,7,)
        dictJournal_Area['Immunity'] = (4,)
        dictJournal_Area['? Journal of Immunology'] = (4,)
        dictJournal_Area['Blood'] = (4,)
        dictJournal_Area['Cell Host & Microbe'] = (4,)
        dictJournal_Area['Structure'] = (5,)
        dictJournal_Area['Neuron'] = (6,)
        dictJournal_Area['? Journal of Biological Chemistry'] = (5,)
        dictJournal_Area['Nature Neuroscience'] = (6,)
        dictJournal_Area['? Journal of Neuroscience'] = (6,)
        dictJournal_Area['? Journal of Experimental Medicine'] = (7,)
        dictJournal_Area['? Journal of Clinical Research'] = (7,)
        dictJournal_Area['? New England Journal of Medicine'] = (7,)
        dictJournal_Area['Lancet'] = (7,)
        dictJournal_Area['Cancer Research'] = (3,5,7,)
        dictJournal_Area['PLoS Computational Biology'] = (1,)
    
        return dictJournal_Area

if __name__ == '__main__':

    import doctest
    print doctest.testmod()