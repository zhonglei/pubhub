'''
Functions to send email to subscriber.
Created on May 3, 2014

@author: zhil2
'''

import smtplib
from phInfo import emailInfo, phDbInfo
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from phController import getListArticlePage
from phDatabaseApi import PhDatabase, MysqlConnection
from phTools import singleStrip
import sys

def sendTestMail():
    
    'open server'
    emailServer = smtplib.SMTP(emailInfo['server'], emailInfo['port'])
    emailServer.starttls()
    emailServer.login(emailInfo['user'], emailInfo['password'])
    
    'create message'
    sender = emailInfo['mainEmail']
#     receivers = ['henrylee18@yahoo.com', 'franklin.zhong@gmail.com', 'wanghugigi@gmail.com']
    receivers = ['henrylee18@yahoo.com']
    subject = 'Test #11'
    header = 'To: '
    for receiver in receivers[:-1]:
        header += receiver + ', '
    header += receivers[-1]
    header += '\n' + 'From: ' + sender + '\n' + 'Subject: ' + subject + '\n'
    body = 'This is a test message from ' + sender + '.\n\n'
    message = header + '\n' + body
    
    'send email'
    emailServer.sendmail(sender, receivers, message)
    
    'close server'
    emailServer.quit()
    
def sendListArticleToSubscriber(subscriberId, sinceDaysAgo = 7):
    
    sender = emailInfo['mainEmail']

    'look up subscriber email address'
    phdb = PhDatabase(MysqlConnection(phDbInfo['dbName'],phDbInfo['ip'],
                                      phDbInfo['user'],phDbInfo['password']))
    _, receiver = phdb.selectDistinct('subscriber', ['email'], 
                                      'subscriberId = '+str(subscriberId))
    receiver = singleStrip(receiver)[0]
    phdb.close()
    
    'Create message container - the correct MIME type is multipart/alternative'
    msg = MIMEMultipart('alternative')
    msg['Subject'] = '''The latest bioscience hot papers, brought to you by Scooply'''
    msg['From'] = sender
    msg['To'] = receiver
    
    'create message body'
    text = 'Plain text to be added.'
    html = getListArticlePage(subscriberId, sinceDaysAgo, displayType = 'email')

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
    
    'open server'
    emailServer = smtplib.SMTP(emailInfo['server'], emailInfo['port'])
    emailServer.starttls()
    emailServer.login(emailInfo['user'], emailInfo['password'])

    'send email'
    emailServer.sendmail(sender, [receiver], msg.as_string())
    
    'close server'
    emailServer.quit()
    

if __name__ == '__main__':
    
    import doctest
    print doctest.testmod()
    
    'if with argument --doctest-only, skip the rest'
    if len(sys.argv) > 1:
        for a in sys.argv[1:]: 
            if a =='--doctest-only':
                sys.exit()

    #sendTestMail()
    
    subscriberId = 8 # henrylee18@yahoo.com
    sendListArticleToSubscriber(subscriberId) 
    
    print 'Done.'
    
'''

to = 'mkyong2002@yahoo.com'
gmail_user = 'mkyong2002@gmail.com'
gmail_pwd = 'yourpassword'
smtpserver = smtplib.SMTP("smtp.gmail.com",587)
smtpserver.ehlo()
smtpserver.starttls()
smtpserver.ehlo
smtpserver.login(gmail_user, gmail_pwd)
header = 'To:' + to + '\n' + 'From: ' + gmail_user + '\n' + 'Subject:testing \n'
print header
msg = header + '\n this is test msg from mkyong.com \n\n'
smtpserver.sendmail(gmail_user, to, msg)
print 'done!'
smtpserver.close()

'''