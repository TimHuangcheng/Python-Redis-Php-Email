#!/usr/bin/python
# -*- coding: utf-8 -*-  
import email
import mimetypes
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
import smtplib 
from email.header import Header
def sendEmail(authInfo, fromAdd, toAdd, subject, plainText, htmlText): 
        strFrom = fromAdd
        #if isinstance(toAdd,list) :
        #    strTo = ', '.join(toAdd) 
        #else :
        strTo = toAdd
        server = authInfo.get('server')
        user = authInfo.get('user')
        passwd = authInfo.get('password') 
        if not (server and user and passwd) :
                print 'incomplete login info, exit now'
                return 
        # 设定root信息
        msgRoot = MIMEMultipart('related')
        msgRoot['Subject'] = subject
        h = Header('Etekcitizen','utf-8')
        h.append('<'+strFrom+'>', 'ascii')
        msgRoot['From'] = h
        msgRoot['To'] = strTo
        print strTo , user , server
        msgRoot.preamble = 'This is a multi-part message in MIME format.' 
        # Encapsulate the plain and HTML versions of the message body in an
        #'alternative' part, so message agents can decide which they want to display.
        msgAlternative = MIMEMultipart('alternative')
        msgRoot.attach(msgAlternative) 
        #设定纯文本信息
        #msgText = MIMEText(plainText, 'plain', 'utf-8')
        #msgAlternative.attach(msgText) 
        #设定HTML信息
        msgText = MIMEText(htmlText, 'html', 'utf-8')
        msgAlternative.attach(msgText) 
        #设定内置图片信息
        #fp = open('test.jpg', 'rb')
        #msgImage = MIMEImage(fp.read())
        #fp.close()
        #msgImage.add_header('Content-ID', '<image1>')
        #msgRoot.attach(msgImage) 
        try :
            #发送邮件
            smtp = smtplib.SMTP()
            #设定调试级别，依情况而定
            smtp.set_debuglevel(0)
            smtp.connect(server)
            smtp.login(user, passwd)
            smtp.sendmail(strFrom, strTo, msgRoot.as_string())
            smtp.quit()
            return True;
        except Exception, e:
            file = open('error.txt','a')
            file.write(time.strftime('%Y-%m-%d %H:%M:%S') + str(e))
            file.write('\n-------------\n')
            file.close()
            return False;
if __name__ == '__main__':
        authInfo = {}
        authInfo['server'] = ''
        authInfo['user'] = ''
        authInfo['password'] = ''
        fromAdd = ''
        toAdd = ['email@qq.com', 'email@163.com']
        subject = '邮件主题'
        plainText = '这里是普通文本'
        htmlText = '<B>HTML文本</B>'
        sendEmail(authInfo, fromAdd, toAdd, subject, plainText, htmlText)