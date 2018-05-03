#!/usr/bin/python
# -*- coding: UTF-8 -*-

## requirement 
# pip install docker
import docker

class customDcoker(object):
    def __init__(self,url,timeout):
        self.client = docker.DockerClient(base_url=url,version='auto',timeout=timeout)
        self.insecure_registry = 'http://172.28.1.103:5000'
    
    def do_something(self):
        pass




def ImagesRepush(url,image,tag):
    insecure_registry = 'http://172.28.1.103:5000'
    client = docker.DockerClient(base_url=url,version='auto',timeout=10)
    images = '%s:%s' % (image,tag)
    for line in client.images.push(images,stream=True,insecure_registry=insecure_registry):
        print line

