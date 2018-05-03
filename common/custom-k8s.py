#!/usr/bin/python
# -*- coding: UTF-8 -*-
import httplib
import json

class customK8s(object):
    def __init__(self,hostname,port,timeout):
        self.conn = httplib.HTTPConnection(hostname, port, timeout)
    def getStatus(self,isolation,service=None):
        if service is not None:
            path = '/api/v1/pods?labelSelector=serviceName=%s,isolationName=%s' % (service,isolation)
        else:
            path = '/api/v1/pods?labelSelector=isolationName=%s' % (isolation)
        result = {}
        try:
            self.conn.request('GET', path)
            resp = self.conn.getresponse()
            result = json.load(resp)
            self.conn.close()
        except BaseException, e:
            print e
            self.conn.close()
        return result

    def getFailreason(self,service):
        isolation = 'base_isolation'
        try:
            result = self.getStatus(isolation,service)
            result = result['items'][0]['status']['containerStatuses'][0]['state']
            reasons = str(result)
            return reasons
        except IndexError, e:
            result = self.getStatus(isolation,'ued_all_static_serv')
            result = result['items'][0]['status']['containerStatuses'][0]['state']
            reasons = str(result)
            #return reasons
            return '%s/ued_all_static update fail! ued_all_static_serv status: %s' % (service,reasons)
    def getFailservs(self,isolation):
        re = self.getStatus(isolation)
        for item in re['items']:
            line = item['status']['containerStatuses'][0]
            if 'running' not in line['state'] or line['restartCount'] > 100:
                yield line


def test1():
    t = zhe800K8s('172.28.1.115','4705','40')
    for line in t.getFailservs('base_isolation'):
        #print line['name'],line['restartCount'],line['state']
        print line['image'].split('-')[1]
        print line


if __name__ == '__main__':
    test1()
