#!/usr/bin/python
#version 2.0
#manager config  by zookeeper 


from configmanage import ConfigManager
import os,shutil
import datetime,time
from ftplib import FTP,error_perm,all_errors
import logging,sys

logger = logging.getLogger("Wangan")
formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')
file_handler = logging.FileHandler("wangan.log")
file_handler.setFormatter(formatter)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.formatter = formatter
logger.addHandler(file_handler)
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)



class Ftpupload(object):
    '''ftp upload'''
    def __init__(self,host,user,passwd,timeout):
        self.ftp = FTP(host)
        self.ftp.login(user,passwd,timeout)
        self.rootpath = self.ftp.pwd()
        #self.ftp.set_debuglevel(2)

    def create_dir(self,abpath):
        '''param abpath : /home/webuser/wangan/20180305/WA_SOURCE_0035/1608'
           '''  
        logger.info('try to create remote ftp dir %s',abpath)
        relatepath = ''
        self.ftp.cwd(self.rootpath)
        for path in abpath.split('/')[4:]:
            try:
                path = path + '/'
                relatepath += path
                self.ftp.mkd(relatepath)
            except all_errors as why:
                pass
        try:
            self.ftp.cwd(relatepath)
            return True
        except error_perm as why:
            logger.exception('faile to create and cwd dir !')
            return False

    def close(self):
        self.ftp.quit()

    def uploadfile(self,remotepath,localfilepath):
        logger.info('begin to upload %s',localfilepath)
        bufsize = 1024
        state = None
        filename = localfilepath.split('/')[-1:][0]
        with open(localfilepath,'rb') as fp:
            if self.create_dir(remotepath):
                try:
                    self.ftp.storbinary('STOR '+filename,fp,bufsize)
                    logger.info('%s upload done',localfilepath)
                except all_errors as why:
                    logger.exception('%s upload failue',localfilepath)
                    state = why
        state = state or 'successfuly'
        return state


class Wangan(object):
    '''scan dest log dir 1/m and upload to wangan'''
    def __init__(self,appname):
        self.q = []
        self.config = ConfigManager(logger=logger)
        self.appname = appname
        self.scan(first_scan=True)


    @property
    def get_config(self):
        return self.config
    
    def backupfile(self,abfile):
        back_dir = self.config.get_configvalue(self.appname,'back_dir')
        src_dir = self.config.get_configvalue(self.appname,'src_dir')
        backfile = abfile.replace(src_dir,back_dir)
        logger.info('begin to backup %s to %s ',abfile,backfile)
        end = backfile.rfind('/')
        try:
            os.makedirs(backfile[0:end])
        except OSError as why:
            logger.warn('%s',why)
        try:
            shutil.move(abfile,backfile)
        except :
            logger.exception('%s backup failed',abfile)
                 
    def scan(self,first_scan=False):
        daydir = src_dir = self.config.get_configvalue(self.appname,'src_dir')
        if not first_scan:
            logger.info('begin to scan logdir %s',src_dir)
            daytime = datetime.datetime.now().strftime("%Y%m%d")
            daydir = os.path.join(src_dir,daytime)
            for dir in os.listdir(src_dir):
                if dir != daytime:
                    logger.info('try to clean expired logdir %s to /tmp',dir)
                    shutil.move(os.path.join(src_dir,dir),'/tmp')  # need test  O(c)
        else:
            logger.info('the first time to scan logdir %s',src_dir)
        for path2file,dirname,filename in os.walk(daydir):
            if filename and  path2file not in self.q:
                self.q.append(path2file)
                logger.info('find logdir %s add it to queue',path2file)

    def upload(self,path2file):
        upload_info = {}
        ftpuploader = Ftpupload(self.config.get_configvalue(self.appname,'ftp_serv'),
                                self.config.get_configvalue(self.appname,'user'),
                                self.config.get_configvalue(self.appname,'passwd'),
                                self.config.get_configvalue(self.appname,'timeout'))
        for abfile in [ os.path.join(path2file,filename) for filename in os.listdir(path2file)]:
            print abfile
            upload_info['filesize'] = os.path.getsize(abfile)
            upload_info['filepath'] = abfile
            result = ftpuploader.uploadfile(path2file,abfile)
            upload_info['state'] = result
            self.backupfile(abfile) 
            #self.writeinfo(upload_info)

    def go(self):
        while self.q:
            path2file = self.q.pop()
            self.upload(path2file)

def main():
    wanganer = Wangan('wangan_task')
    while True:
        wanganer.go()
        sleeptime = wanganer.get_config.get_configvalue('wangan_task','scan_interval',is_watch=True)
        logger.info('wait the next sacn interval %s s',sleeptime)
        time.sleep(int(sleeptime))
        wanganer.scan()

if __name__ == '__main__':
    main()

