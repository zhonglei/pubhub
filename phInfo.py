'''
Administrative information.

Created on Apr 30, 2014

@author: zhil2
'''

webServerInfo = {'addr':'www.scooply.info',}

phDbInfo = {'dbName':'pubhub', 'ip':'54.187.112.65', 'user':'root', 
          'password':'lymanDelmedio123'}

testDbInfo = {'dbName':'doctest', 'ip':'54.187.112.65', 'user':'root', 
            'password':'lymanDelmedio123'}

emailInfo = {'server':'smtp.gmail.com', 'port':587, 'user':'pubhub2@gmail.com', 
           'password':'lymanDelmedio123', 'mainEmail':'scooply@scooply.info',
           }

'''when a new subscriber joins, how many seconds in Pubmed history we backtrack
to get his article records'''
pubmedBacktrackSecondForNewSubscriber = 7 * 24 * 3600

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
    def getListGeneralJournal():
        l=[]
        l.append('Nature')
        l.append('Cell')
        l.append('Science')
        
        return l
    
    @staticmethod
    def getDictJournal_Area():
        dictJournal_Area={}
        dictJournal_Area['Nature'] = (1,2,3,4,5,6,7,)
        dictJournal_Area['Cell'] = (1,2,3,4,5,6,7,)
        dictJournal_Area['Science'] = (1,2,3,4,5,6,7,)
        dictJournal_Area['Nature Genetics'] = (1,2,3,4,5,6,7,)
        dictJournal_Area['Curr Biol.'] = (1,2,3,4,5,6,)
        dictJournal_Area['EMBO J.'] = (1,2,3,4,5,6,7,)
        dictJournal_Area['Proc. Natl. Acad. Sci. U.S.A.'] = (1,2,3,4,5,6,7,)
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
        dictJournal_Area['Nucleic Acids Res.'] = (1,2,5,)
        dictJournal_Area['Biophysical Journal'] = (2,)
        dictJournal_Area['Development'] = (3,)
        dictJournal_Area['PLoS Biology'] = (1,2,3,4,5,6,7,)
        dictJournal_Area['PLoS Medicine'] = (7,)
        dictJournal_Area['PLoS Genetics'] = (1,2,3,4,5,6,7,)
        dictJournal_Area['Immunity'] = (4,)
        dictJournal_Area['J Immunol'] = (4,)
        dictJournal_Area['Blood'] = (4,)
        dictJournal_Area['Cell Host & Microbe'] = (4,)
        dictJournal_Area['Structure'] = (5,)
        dictJournal_Area['Neuron'] = (6,)
        dictJournal_Area['J Biol Chem.'] = (5,)
        dictJournal_Area['Nature Neuroscience'] = (6,)
        dictJournal_Area['J. Neurosci.'] = (6,)
        dictJournal_Area['J Exp Med.'] = (7,)
        dictJournal_Area['J Clin Invest.'] = (7,)
        dictJournal_Area['N Engl J Med'] = (7,)
        dictJournal_Area['Lancet'] = (7,)
        dictJournal_Area['Cancer Research'] = (3,5,7,)
        dictJournal_Area['PLoS Computational Biology'] = (1,)
    
        return dictJournal_Area

if __name__ == '__main__':

    import doctest
    print doctest.testmod()