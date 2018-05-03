#!/usr/bin/python
#coding:utf-8

#auth ell
#Need to improve the code for loom (Service discovery by Zookeeper)
####requirement###########
#kazoo 2.1
#python 2.7 2.6

from AbstractZookeeperClient import *
from kazoo.client import KazooClient,DataWatch,ChildrenWatch
from kazoo.exceptions import NoNodeException,NodeExistsException,KazooException
import logging
import os
import socket
import fcntl

class Constants(object):
    ZOOKEEPER_ROOT_PATH = '/conf'
    DEFAULT_PRODUCTION_ZKADDRESS = "127.0.0.1:2181"
    ZOOKEEPER_TIMEOUT = 3
    ZOOKEEPER_DOMAIN = 'zk.domain.net'
    APP_TYPE_PUBLIC = 'public'
    APP_TYPE_COMMON = 'common'
    IMAGO_FILE_SNAPSHOT_PATH = os.environ['HOME'] + '/.conf/conf_snapshot'

    
class ConfigManager(object):
    '''manager configurations  by zookeeper'''
    def __init__(self,logger,serverlist=None):
        self._logger = logger
        self.localCacheDict = {}
        self.WatchDict = {}
        self.initAppKeyDict = {}
        self.PublicAppKeyDict = {}
        self.serverlist = serverlist or  self.getImagoZkAddress()
        self.snapshotPath = Constants.IMAGO_FILE_SNAPSHOT_PATH
        try:
            self.zk = AbstractZookeeperClient(self.serverlist,self._logger,Constants.ZOOKEEPER_TIMEOUT)
            self._iszktimeout = False
        except Exception as why:
            self._logger.error('connect to zookeeper %s, will load local_snapshot',why)
            self._read_snapshot()
            self._iszktimeout = True

    @staticmethod
    def writefile(fileSnapshot,kvlist):
        with open(fileSnapshot,'w') as fp:
            for kv in kvlist:
                fp.write(kv)
                fp.write('\n')

    def getImagoZkAddress(self):
        '''get zookeeper address by dns'''
        serverList = ""
        try:
            serverList = socket.gethostbyname_ex(Constants.ZOOKEEPER_DOMAIN)[2]
            serverList= ','.join(map(lambda x:x+':2181',serverList))
        except (socket.gaierror,socket.herror) as why:
            self._logger.error('Parse zk.domain.net error,will loading default zookeeper address of prod %s',why)
            serverList = Constants.DEFAULT_PRODUCTION_ZKADDRESS
        return serverList

    def iszktimeout(self):
        if self._iszktimeout: return True
        if self.zk.iszktimeout : return True

    def _read_snapshot(self):
        '''load loacl snapshaot of configurations'''
        self._logger.info('loading file snapshot to local cache!')
        if os.path.isdir(self.snapshotPath) and os.path.exists(self.snapshotPath):
            filelist = [ filename for filename in os.listdir(self.snapshotPath) if os.path.isfile(os.path.join(self.snapshotPath,filename)) ]
            for snapshotfile in filelist :
                if snapshotfile.endswith('.properties'):
                    cacheKeyPrefix = os.path.join(Constants.ZOOKEEPER_ROOT_PATH,snapshotfile.replace('.properties',''))
                    with open(self.snapshotPath+'/'+snapshotfile,'r') as f:
                        for line in f.readlines():
                            (key,value) = line.split('=')
                            self._update_localcache(cacheKeyPrefix+'/'+key,value)
    
    def _update_localcache(self,cachekey,cachevalue):
        '''update localcache of configurations'''
        self.localCacheDict[cachekey] = cachevalue

    def _datawatch_handle(self,data,stat,event):
        '''callback func for datawatch 
          what about del event ?'''
        if event:
            watchKey = event[2]
            self.localCacheDict[watchKey] = data

    def _childwatch_handle(self,children,event):
        '''Need to improve the code for Loom'''
        if event:
             watchChild = event[2]
             pass  

    def get_appconfigvalue(self,appkey,is_watch=False):
        '''hight-level ChildrenWatch ,return kvs of parent's node;
           Need to improve the code for loom (Service discovery by Zookeeper) '''
        if not self.iszktimeout():
            configValue = {}
            appPath = os.path.join(Constants.ZOOKEEPER_ROOT_PATH,appkey)    
            if appPath not in self.WatchDict:
                if is_watch:
                    ChildrenWatch(self.zk.client,appPath,self._childwatch_handle,send_event=True)
                    self.WatchDict[appPath] = True
            if appkey not in self.initAppKeyDict:
                self.loadconfig_byappKey_fromzk(appkey)
                self.initAppKeyDict[appkey] = True
        for key,value in self.localCacheDict.iteritems():
             if appkey == key.split('/')[2]:
                 configKey = key.split('/')[-1]
                 configValue[configKey] = value
        return configValue

    def get_configvalue(self,appkey,configkey,defaultvalue=None,is_watch=False):
        '''hight-level DataWatch, return the configvalue of the key'''
        configPath = os.path.join(Constants.ZOOKEEPER_ROOT_PATH,appkey,configkey)
        if not self.iszktimeout():
            if configPath not in self.WatchDict: 
                # first watch and add it ;will  not fire event
                if is_watch:
                    DataWatch(self.zk.client,configPath,self._datawatch_handle) 
                    self.WatchDict[configPath] = True
              # if not load conf then init it
            if appkey not in self.initAppKeyDict:
                self.loadconfig_byappKey_fromzk(appkey)
                self.initAppKeyDict[appkey] = True
        configvalue = self.localCacheDict[configPath]
        return configvalue if configvalue else defaultvalue

    def loadconfig_byappKey_fromzk(self,appkey):
        # init local snapshot file
        self._create_snapshot(appkey)
        #init local cache
        appPath = Constants.ZOOKEEPER_ROOT_PATH + '/' +appkey
        configDict = self.zk.get_kvmap_byparent(appPath) 
        if configDict :
            for key in configDict:
                dataPath = appPath + '/' + key
                self.localCacheDict[dataPath] = configDict[key]
         
    def _create_snapshot(self,appkey):
        '''create local snapshot '''
        #fcntl.flock
        fileSnapshot = os.path.join(Constants.IMAGO_FILE_SNAPSHOT_PATH,appkey+'.properties')
        fileLock = fileSnapshot + '.lock'
        appPath = os.path.join(Constants.ZOOKEEPER_ROOT_PATH,appkey)
        try:
            os.makedirs(Constants.IMAGO_FILE_SNAPSHOT_PATH)
        except OSError as why:
            self._logger.warn('%s',why)
        configMap = self.zk.get_kvlist_byparent(appPath)
        if configMap:
            fp = open(fileLock,'w+')
            try:
                fcntl.lockf(fp,fcntl.LOCK_EX|fcntl.LOCK_NB)
                self.writefile(fileSnapshot,configMap)
                self._logger.info('file sbapshot %s create',fileSnapshot)
            except Exception as why:
                self._logger.info('%s locking conflict %s' % (fileLock,why))
                
            finally:
                fp.close()
    @property       
    def get_localcache(self):
        return self.localCacheDict

    @property
    def get_localinitinfo(self):
        info = {}
        info['initapp'] = self.initAppKeyDict.keys()
        info['watchkey'] = self.WatchDict.keys()
        return info 
        

def test():
    import time,sys
    logger = logging.getLogger()
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.formatter = formatter
    logger.addHandler(console_handler)
    logger.setLevel(logging.INFO)
    config = ConfigManager(logger=logger)
    while True:
        print config.get_configvalue('test-serv','zookeeper.connection.timeout.ms',is_watch=True)
        time.sleep(10)
        print config.get_localcache
        print config.get_localinitinfo
if __name__ == '__main__':
    test()








