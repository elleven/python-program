#!/usr/bin/python
#version 1.0
#pip install timeout-decorator
import os
import socket
from  datetime import datetime,timedelta,date
from ftplib import FTP,error_perm,all_errors
import logging,sys
import re
import gzip
import shutil

logger = logging.getLogger("log-collector")
formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')
file_handler = logging.FileHandler("/data0/scripts/log-collector-nginx.log")
file_handler.setFormatter(formatter)
#console_handler = logging.StreamHandler(sys.stdout)
#console_handler.formatter = formatter
logger.addHandler(file_handler)
#logger.addHandler(console_handler)
logger.setLevel(logging.INFO)

CONFIG_DEFAULT = {
    'ftp_serv': '127.0.0.1',
    'user': 'logcollector',
    'passwd': '',
    'timeout': 60,
    'logdir': '/data0/logs/nginx/gzip',
    'bufsize': 1024
}

class Ftpupload(object):
    '''ftp upload'''
    def __init__(self,host,user,passwd,timeout,bufsize):
        self.ftp = FTP(host)
        self.ftp.login(user,passwd,timeout)
        self.rootpath = self.ftp.pwd()
        #self.ftp.set_debuglevel(2)
        self.bufsize = bufsize
    def create_dir(self,destpath):
        '''param destpath : /www.laohu8.com/{{hostname}}/www.laohu8.com.access.log-2019-01-04.log.gz
           '''
        try:
            self.ftp.cwd(destpath)
        except all_errors as why:
            relatepath = ''
            self.ftp.cwd(self.rootpath)
            for path in destpath.split('/'):
                try:
                    path = path + '/'
                    relatepath += path
                    self.ftp.mkd(relatepath)
                except error_perm as why:
                    pass
            self.ftp.cwd(relatepath)
    def close(self):
        self.ftp.quit()
    def uploadfile(self,destpath,localpath):
        '''param destpath:  /www.laohu8.com/{{hostname}}/www.laohu8.com.access.log-2019-01-04.log.gz
                 localpath: /data0/logs/nginx/gzip/www.laohu8.com.access.log-2019-01-04.log.gz
            '''
        filename = localpath.split('/')[-1:][0]
        with open(localpath,'rb') as fp:
            try:
                self.create_dir(destpath)
                self.ftp.storbinary('STOR '+filename,fp,self.bufsize)
                logger.info('%s upload done',localpath)
            except all_errors as why:
                logger.exception('%s upload failue',localpath)

class collector(object):
    '''scan dest log dir and upload to log-center'''
    def __init__(self,regx):
        self.q = []
        self.config = CONFIG_DEFAULT
        self.node = socket.gethostname()
        self.scan_nginx(regx)

    def scan_nginx(self,regx):
        for path,dir_l,file_l in os.walk(self.config['logdir']):
            if len(file_l) > 0:
                self.q += [ os.path.join(path,file_n) for file_n in file_l if re.match(regx,file_n)]

    def upload(self,path2file):
        ftpuploader = Ftpupload(self.config['ftp_serv'],
                                self.config['user'],
                                self.config['passwd'],
                                self.config['timeout'],
                                self.config['bufsize'])
        domain_n = '.'.join(path2file.split('/')[-1].split('.')[0:3])
        destpath = os.path.join('/stock-nginx',domain_n,self.node)
        ftpuploader.uploadfile(destpath,path2file)

    def go(self):
        while self.q:
            path2file = self.q.pop()
            self.upload(path2file)

def main():
    YESTERDAY = date.today() + timedelta(days=-1)
    YY,MM,DD = YESTERDAY.isoformat().split('-')
    #regx = re.compile(r".*(laohu8\.com|tigerbbs\.com).*log-%s-%s-%s\.log\.gz" % (YY,MM,DD))
    regx = re.compile(r".*(laohu8\.com|tigerbbs\.com).*log-2019.*\.log\.gz")
    log_collector = collector(regx)
    log_collector.go()

if __name__ == '__main__':
    main()
