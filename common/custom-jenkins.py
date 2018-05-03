#!/usr/bin/python 
# -*- coding: UTF-8 -*-
from jenkinsapi import *
import re
import sys

class customJenkins(object):
    def __init__(self,url,username=None,password=None):
        self.url = url
        self.server = jenkins.Jenkins(self.url,username=username,password=password)
    def buildJob(self,jobname):
        self.server.build_job(jobname)
    def getJobStatus(self,jobname):
        if self.server[jobname].is_running():
                return 'ok'
        elif self.server[jobname].is_queued_or_running():
            return 'jon is queue'
        else:
            return self.server[jobname].is_running()
    def getLastBuildNumber(self,jobname):
        return self.server[jobname].get_last_buildnumber()
    def getLastFailedBUildNumber(self,jobname):
        return self.server[jobname].get_last_failed_buildnumber()
    def getStatus(self, jobno,jobname):
        try:
                myBuild = self.server[jobname].get_build(jobno)
                return myBuild.get_status()
        except KeyError:
                print "Build number: %s is not existed" % jobno
                return False
    def getJobsList(self):
        jobs_list = self.server.get_jobs()
        return jobs_list
    def getUsername(self, jobno,jobname):
        try:
                print '++++',self.server[jobname],'++++'
                myBuild = self.server[jobname].get_build(jobno)
        except KeyError:
                print "Build number: %s is not existed" % jobno
                return False
        else:
                print myBuild.get_causes()[0]['userName']

    def getBuildTime(self, jobno,jobname):
        myBuild = self.server[jobname].get_build(jobno)
        return myBuild.get_timestamp()

    def getConsole(self, jobno,jobname):
        myBuild = self.server[jobname].get_build(jobno)
        return myBuild.get_console()
    def getResulturl(self,jobno,jobname):
        myBuild = self.server[jobname].get_build(jobno)
        return myBuild.get_result_url()
    def stopJob(self,jobno,jobname):
        if self.server[jobname].stop(jobno):
            print 'running'
        else:
            print 'stop'
    def viewXml(self,jobname):
        xmlResult = self.server[jobname].get_config().encode('utf-8')
        return xmlResult
    def updateXml(self,jobname,context):
        self.server[jobname].update_config(context,full_response='True')
    def copyJob(self,oldjob,newjob):
        self.server.copy_job(oldjob,newjob)
    def deleJob(self,jobname):
        self.server.delete_job(jobname)
    def existJob(self,jobname):
        return  self.server.has_job(jobname)
    def getfailreason(self,jobname):
        reload(sys)
        sys.setdefaultencoding('utf-8')

        lastfailnum = self.getLastFailedBUildNumber(jobname)
        console = self.getConsole(lastfailnum,jobname)
        resulturl = self.getResulturl(lastfailnum,jobname)
        pat = re.compile('(.*)(ERROR|failure|no such file or directory)(.*)')
        result = []
        reason = '\n'
        for line in console.split('\n'):
            m = pat.search(line)
            if m: result.append(m.group(0))
        result = [reason.join(result),resulturl]

        return result
