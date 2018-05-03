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
                  
class zhe800Registry(Http_Common):
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


white_image_lists = [u'ued_all_static_serv_redis',u'base/elasticsearch', u'base/imago-admin', u'base/java', u'base/loom-admin', u'base/nginx', u'base/nginx_static', u'base/node', u'base/openresty', u'base/ruby', u'base/tomcat', u'base/ued-nginx', u'base/zhe800gateway', u'base/zookeeper-cluster', u'base/zookeeper-imago', u'base_couchbase', u'base_fdfs', u'base_kafka_manager', u'base_memcached', u'base_otter', u'base_redis-sentry', u'base_redis6379', u'base_redis6380', u'base_tao800_fire', u'base_zhe800_zhaoshang', u'base_zhebuy_task', u'centos6.5_x86_64-base', u'eagleye-admin', u'eagleye-admin-base', u'eagleye-collector', u'eagleye-collector-base', u'eagleye_admin', u'eagleye_admin_base', u'eagleye_adminv1', u'eagleye_collector', u'eagleye_collector_base', u'env-task', u'galaxy/arch-green', u'galaxy/busybox', u'galaxy/checker-green', u'galaxy/dns-etcd', u'galaxy/exechealthz', u'galaxy/faketime', u'galaxy/fileserver-green', u'galaxy/galaxy-green', u'galaxy/hubble-green', u'galaxy/hyperkube-green', u'galaxy/kube2sky', u'galaxy/kubernetes-dashboard', u'galaxy/lb-green', u'galaxy/loommanager-green', u'galaxy/mysql-taskengine', u'galaxy/netdata-green', u'galaxy/pause', u'galaxy/registry', u'galaxy/skydns', u'galaxy-admin', u'imago-admin', u'java', u'kafka-cluster', u'kafka_manager', u'nginx-ued', u'nginx_ldap', u'postgres', u'static-proxy', u'tengine', u'tomcat', u'ubuntu', u'ued_all_static_serv_redis', u'varnish', u'zabbix-agent-public-service-port', u'zedis/redis', u'zookeeper-cluster', u'zookeeper-cluster-base',u'tigase',u'shangcheng_erp_doc',u'cd_ued_zhe_statics_redis',u'tao800_fire_sidekiq_all_in_one_redis',u'zhe800_zhaoshang_sidekiq_all_in_one_redis']

base_image_lists = ['base_zhe800_zhaoshang','base_zhebuy_task','base_tao800_fire']

def comp(x,y):
    try:
        x = int(x.split('-')[-1])
        y = int(y.split('-')[-1])
    except ValueError:
        print x,y
    if x < y:
        return 1
    if x > y:
        return -1
    else:
        return 0

def get_white_tag_sets(image):
    white_map = {}
    with open('./WhiteListFile.txt') as f:
        for line in f:
            key = line.split(',')[0]
            value = line.split(',')[1].replace('\n','').split('|')[:]
            white_map.setdefault(key,value)
    if image in white_map:
        white_tag_set = set(white_map[image])
        return white_tag_set
    else:
        return None

def getallimagestag():
    r = zhe800Registry('172.28.1.103',5000,10)
    allimages = json.loads(r.getImageList())['repositories']
    for image in allimages:
        tags = json.loads(r.getImageTag(image))['tags'] or []
        if len(tags) > 3:
            print r.getImageTag(image)

SAVE_TAGS_NUM = 3
def main():
    r = zhe800Registry('172.28.1.103',5000,10)
    allimages = json.loads(r.getImageList())['repositories']
    for image in allimages:
        if image in white_image_lists:
            pass
        else:
            tags = json.loads(r.getImageTag(image))['tags'] or []
            if len(tags) > SAVE_TAGS_NUM:
                try:
                    tags.remove('master')
                except ValueError:
                    pass
                tags.sort(comp)
                want_clean_tags = set(tags[SAVE_TAGS_NUM:])
                white_tag_sets = get_white_tag_sets(image) or set()
                clean_tags = want_clean_tags.difference(white_tag_sets)
                print clean_tags
                #for tag in clean_tags:
                #    	if tag:
                #            digest = r.getTagDigest(image,tag)
                #            print image,tag,r.delImageTag(image,digest)

    

if __name__ == '__main__':
    #getallimagestag()
    main()
