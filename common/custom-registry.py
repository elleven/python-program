#!/usr/bin/python
# -*- coding: UTF-8 -*-
import httplib,urllib
import json

class Http_Common(object):
    def __init__(self,host,port,timeout):
        self.host = host
        self.port = port
        self.timeout = timeout
    def do_request(self,method,path,header,rec_data=True):
        try:
            self.conn = httplib.HTTPConnection(self.host,self.port,self.timeout)
            self.conn.request(method,path,headers=header)
            response = self.conn.getresponse()
            data = None
            if rec_data: data = response.read()
            return response,data
        except httplib.HTTPException as e:
            print e
            self.conn.close()
                  
class customRegistry(Http_Common):
    version = 'application/vnd.docker.distribution.manifest.v2+json'
    def __init__(self,host,port,timeout):
        Http_Common.__init__(self,host,port,timeout)
        self.apiDict = {'manifest':'/v2/%s/manifests/%s' ,
                        'blob':'/v2/%s/blobs/%s'  ,
                        'images':'/v2/_catalog?n=10000' ,
                        'tags':'/v2/%s/tags/list?n=10000' ,
                        'digest':'/v2/%s/manifests/%s',}
        self.header = { 'Accept':zhe800Registry.version }
    def getmanifest(self,image,tag):
        manifest = []
        manifest_api = self.apiDict['manifest'] % (image,tag)
        response = self.do_request('GET',manifest_api,self.header)
        if response[0].status == 200: 
            return response[1]
    def checkBlobs(self,image,digest):
        header = { 'Accept':zhe800Registry.version,'Range':'bytes=0-1' }
        blob_api = self.apiDict['blob'] % (image,digest)
        response = self.do_request('GET',blob_api,header)
        if response[0].status == 404: 
            return True
    def getImageList(self):
        images_api = self.apiDict['images'] 
        response = self.do_request('GET',images_api,self.header)
        if response[0].status == 200:
            return response[1]
        
    def getImageTag(self,image):
        tags_api = self.apiDict['tags'] % (image)
        response = self.do_request('GET',tags_api,self.header)
        if response[0].status == 200:
            return response[1]
    def getTagDigest(self,image,tag):
        digest_api = self.apiDict['digest'] % (image,tag)
        response = self.do_request('HEAD',digest_api,self.header)
        if response[0].status == 200:
            digest = response[0].getheader('docker-content-digest')
            return digest   
    def delImageTag(self,image,digest):
        delete_api = self.apiDict['digest'] % (image,digest)
        response = self.do_request('DELETE',delete_api,self.header)
        return response[0].status,response[0].reason


if __name__ == '__main__':
    pass
