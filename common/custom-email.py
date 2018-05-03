#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import urllib,urllib2
import socket
class customEmail(object):
    def __init__(self,url,username,passwd):
        self.url = url
        self.username = username
        self.passwd = passwd
        #create manager
        passwordMgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passwordMgr.add_password(None,self.url,self.username,self.passwd)
        httpBasicAuthHandler = urllib2.HTTPBasicAuthHandler(passwordMgr)
        self.opener = urllib2.build_opener(httpBasicAuthHandler)
        
    def sendMail(self,subject, content, recivers, sender):
        ipAddr = socket.gethostbyname(socket.gethostname())
        subject = urllib.quote(subject.decode('utf-8').encode('utf-8', 'replace'))
        content = urllib.quote(content.decode('utf-8').encode('utf-8', 'replace'))
        requestURL = '''%s?clientip=%s&sender=%s&reciver=%s&subject=%s&content=%s''' %  (self.url, ipAddr, sender, recivers, subject, content)
        urllib2.install_opener(self.opener)
        response = urllib2.urlopen(requestURL).read()
        return response

if __name__ == '__main__':
    pass
