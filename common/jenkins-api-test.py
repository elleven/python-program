#!/usr/bin/python
# -*- coding=utf-8 -*-

import xml.etree.cElementTree  as ET
import jenkins
import xml.dom.minidom as minidom
import sys

JENKINS_URL = 'http://172.28.49.55:28080'
USER = ''
TOKEN = ''

reload(sys)
sys.setdefaultencoding('utf-8')


def get_service():
    """用于获取 Jenkins 中 job 定义的服务名称以及部署机器列表
       return
       { jobname: hostlists ...}"""
    ret = {}
    J = jenkins.Jenkins(JENKINS_URL, username=USER, password=TOKEN)
    joblists = J.get_all_jobs()
    for job in joblists:
        jobname = job['fullname']
        jobconfig = J.get_job_config(jobname)
        # parse xml
        ConfigTree = ET.fromstring(jobconfig)
        for params in ConfigTree.findall('.//hudson.model.StringParameterDefinition'):
            if params.find('name').text == 'HOST_LISTS':
                hostlists = params.find('defaultValue').text
                if jobname in ret:
                    print 'conflict jobname %s' % jobname
                else:
                    ret.setdefault(jobname, hostlists)
    return ret


if __name__ == '__main__':
    for k,v in get_service().iteritems():
        print k, v
