'''

Methods for sending email to subscribers.

Created on May 3, 2014

@author: zhil2
'''

import sys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time

from phInfo import emailInfo, phDbInfo
from phController import getListArticlePage, getSubscriberEmail
    
def sendListArticleToSubscriber(subscriberId, sinceDaysAgo = 7):
    
    sender = emailInfo['mainEmail']

    receiver = getSubscriberEmail(phDbInfo, subscriberId)
    
    'Create message container - the correct MIME type is multipart/alternative'
    msg = MIMEMultipart('alternative')
    msg['Subject'] = '''This week's bioscience hot papers, brought to you by Scooply'''
    msg['From'] = sender
    msg['To'] = receiver
    
    'create message body'
    text = 'Plain text to be added.'

    now = time.time()
    startTime = now - sinceDaysAgo * 24 * 3600
    endTime = now
    html = getListArticlePage(phDbInfo, startTime, endTime, subscriberId, displayType = 'email')

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
    
#     import doctest
#     print doctest.testmod()
    
    'if with argument --doctest-only, skip the rest'
    if len(sys.argv) > 1:
        for a in sys.argv[1:]: 
            if a =='--doctest-only':
                sys.exit()

    #sendTestMail()
    
    subscriberId = 3
    sinceDaysAgo = 7
    sendListArticleToSubscriber(subscriberId, sinceDaysAgo) 
    
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