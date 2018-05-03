#/usr/bin/python
# -*- coding: UTF-8 -*-

## requirment  
# pip install redis

from redis import *

class Handler(object):
    def callback(self,prefix,name,*args):
        method = getattr(self,prefix+name,None)
        if callable(method): 
            return method(*args)
        else: 
            print "method not found"
    def clean(self,name,*args):
        self.callback('del_large_',name,*args)
    def len(self,name,*args):
        self.callback('len_',name,*args)
class customRedis(Handler):
    def __init__(self,host,port,passwd,db=0):
        self.pool = ConnectionPool(host=host,port=port,db=db,max_connections=300)
        try:
            self.cxn =  StrictRedis(connection_pool=self.pool,password=passwd)
        except (AuthenticationError,ConnectionError),e:
            print e
            raise
    def exist(self,key):
        if self.cxn.exists(key):
            return True
        
    def gettype(self,key):
        return self.cxn.type(key)
    def del_large_string(self,key):
        try:
            self.cxn.delete(key)
        except RedisError,e:
            print e
            return False
        return True
    def del_large_hash(self,hash_key):
        cursor = '0'
        while cursor != 0:
            cursor,data = self.cxn.hscan(hash_key, cursor=cursor, count=500)
            for item in data.items():
                self.cxn.hdel(hash_key, item[0])
    def del_large_set(self,set_key):
        cursor = '0'
        while cursor != 0:
            cursor,data = self.cxn.sscan(set_key, cursor=cursor, count=500)
            for item in data:
                self.cxn.srem(set_key, item)
    def del_large_list(self,list_key):
        while self.cxn.llen(list_key)>0:
            self.cxn.ltrim(list_key,0,-101)
    def del_large_sortedset(self,sortedset_key):
        while self.cxn.zcard(sortedset_key)>0:
            self.cxn.zremrangebyrank(sortedset_key,0,99)
    def len_hash(self,hash_key):
        print  self.cxn.hlen(hash_key)
    def len_list(self,list_key):
        print self.cxn.llen(list_key)
    def len_set(self,set_key):
        print self.cxn.scard(set_key)


if __name__ == '__main__':
    pass




