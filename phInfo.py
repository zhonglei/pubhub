'''
Information stored.

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

if __name__ == '__main__':

    import doctest
    print doctest.testmod()