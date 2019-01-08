#!/usr/bin/python
#version 1.0
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
file_handler = logging.FileHandler("/data0/scripts/log-collector.log")
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
    'logdir': '/data0/logs/',
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
        '''param destpath : /stock-services/172.28.48.88/*.log
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
        '''param destpath: /stock-services/172.28.48.88/*.log
                 localpath: /data0/logs/stock-services/2019/01/06/*2019-01-06.log*
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
        self.scan(regx)

    def scan(self,regx):
        for path,dir_l,file_l in os.walk(self.config['logdir']):
            if re.match(regx,path) and len(file_l) > 0:
                self.q += [ os.path.join(path,file_n) for file_n in file_l ]

    def upload(self,path2file):
        if not path2file.endswith('log.gz'):
            logger.info('gzip %s ',path2file)
            self.gzip_file(path2file)
            path2file = path2file +  '.gz'
        ftpuploader = Ftpupload(self.config['ftp_serv'],
                                self.config['user'],
                                self.config['passwd'],
                                self.config['timeout'],
                                self.config['bufsize'])
        serv_n = path2file.split('/')[3]
        destpath = '/' + serv_n + '/' +self.node
        ftpuploader.uploadfile(destpath,path2file)

    def gzip_file(self,s_file,d_file=None):
        f_in = open(s_file,'rb')
        f_out = gzip.open(s_file + '.gz','wb')
        shutil.copyfileobj(f_in,f_out)
        f_in.close()
        f_out.close()
        os.remove(s_file)

    def go(self):
        while self.q:
            path2file = self.q.pop()
            self.upload(path2file)

def main():
    YESTERDAY = date.today() + timedelta(days=-1)
    YY,MM,DD = YESTERDAY.isoformat().split('-')
    #regx = re.compile(r"^/data0/logs/stock-.*/%s/%s/%s" % (YY,MM,DD))
    regx = re.compile(r"^/data0/logs/stock-.*/2018/.*")
    log_collector = collector(regx)
    log_collector.go()

if __name__ == '__main__':
    main()
