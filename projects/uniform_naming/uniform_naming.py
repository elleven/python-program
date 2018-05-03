#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import ConfigParser,glob
import xmlrpclib,supervisor.xmlrpc
import psutil
import os,sys,signal,time
# pip install psutil




class zhe800Supervisor(object):
    def __init__(self,socket):
        self.s = xmlrpclib.ServerProxy('http://127.0.0.1',transport=supervisor.xmlrpc.SupervisorTransport(
                None,None,'unix://' + socket ))
    def getProcessChildPid(self,name):
        pid = self.s.supervisor.getProcessInfo(name)['pid']
        if pid == 0:
            child_pid = []
        else:
            child_pid = [ child.pid for child in psutil.Process(pid).children() ]
        return child_pid
    def stopProgram(self,name):
        child_pid = self.getProcessChildPid(name)
        if len(child_pid) > 0:
            self.s.supervisor.stopProcess(name,False)
            for pid in child_pid:
                print 'find child process %s ,ready to kill ..' % pid
                os.kill(int(pid),signal.SIGTERM)
        else: 
            try:
                self.s.supervisor.stopProcess(name,False)
            except xmlrpclib.Fault,e:
                print e
    def update(self):
        result = self.s.supervisor.reloadConfig()
        for rmitem in result[0][2]:
            self.s.supervisor.removeProcessGroup(rmitem)
            print '%s stopped' % rmitem
        for additem in result[0][0]:
            self.s.supervisor.addProcessGroup(additem)
            print '%s updated process group' % additem
    def check_status(self,name):
        print '%s check %s' % (name,self.s.supervisor.getProcessInfo(name)['statename'])
        print self.s.supervisor.tailProcessStdoutLog(name,1,600)
        
class reconfer(object):
    def __init__(self,oname,nname):
        self.defaultpaths = '/etc/'
        self.defaultconf = 'supervisord.conf'
        self.oname = oname
        self.nname = nname
        self.is_spilt = None
        self.defaultsplitpath = None
        self.parser = None
    def loadConf(self):
        parser = ConfigParser.ConfigParser()
        try:
            parser.read(self.defaultpaths + self.defaultconf)
        except ConfigParser.ParsingError, why:
            raise ValueError(str(why))
        if not parser.has_section('program:' + self.oname) and  parser.has_section('include'):
            files = parser.get('include', 'files')
            files = self.defaultpaths + files
            filenames = glob.glob(files)   
            for filename in filenames:
                #if self.oname in filename :  
                if self.oname + '.ini' == filename.split('/')[-1] :
                    oparser = ConfigParser.ConfigParser() 
                    oparser.read(filename)
                    self.is_spilt = False
                    self.defaultsplitpath = filename
                    return oparser
            raise ValueError('not found program %s' % self.oname) 
        else:
            self.is_spilt = True
            self.defaultsplitpath =  '/etc/supervisord.conf'
            return parser
    def writeNewConf(self,nconfdict):
        if nconfdict:
            include = '/etc/supervisord.d'
            nfilename = include + '/' + self.nname + '.ini'
            nparser = ConfigParser.ConfigParser()
            nparser.add_section('program:' + self.nname)
            for key in nconfdict:
                nparser.set('program:' + self.nname,key,nconfdict[key])
            nparser.write(open(nfilename,'w'))
            print 'Write new conf %s ..' % nfilename
            return True
    def do_reconf(self):
        def replace(d,oname,nname):
            newconfdict = {}
            for key in d:
                newconfdict.setdefault(key,d[key].replace(oname,nname,1))
            return newconfdict   
        oparser = self.loadConf()
        print 'Conf Loading %s ..' % self.defaultsplitpath
        if 'program:' + self.oname in oparser.sections():
            oconfdict = dict(oparser.items('program:' + self.oname))
            nconfdict = replace(oconfdict,self.oname,self.nname)
            if self.is_spilt is True:
                if self.writeNewConf(nconfdict):
                    oparser.remove_section('program:' + self.oname)
                    print 'rm old conf from %s' % self.defaultsplitpath
                    oparser.write(open(self.defaultsplitpath,'w'))
            elif self.is_spilt is False:
                if self.writeNewConf(nconfdict) and os.path.isfile(self.defaultsplitpath):
                    os.remove(self.defaultsplitpath)
                    print 'rm old conf from %s' % self.defaultsplitpath 
            print 'mv %s to %s' % (oconfdict['directory'],nconfdict['directory'])
     # remove dir shell      
            os.rename(oconfdict['directory'].replace('shell',''),nconfdict['directory'].replace('shell',''))
            return True
        else:
            raise ValueError('program:%s not in conf:%s' % (self.oname,self.defaultsplitpath))
            

def test_reconfer():
    confer = reconfer('wris-msgcenter-thrift','wris_msgcenter_thrift')     
    confer.do_reconf()
def get_socket_path():
    parser = ConfigParser.ConfigParser()
    parser.read('/etc/supervisord.conf')
    socket_path = parser.get('unix_http_server','file')
    return socket_path
def main():
    UNC = reconfer(sys.argv[1],sys.argv[2])
    rb = zhe800Supervisor(get_socket_path())
  #reconf
    UNC.do_reconf()
   # update
    rb.stopProgram(sys.argv[1])
    time.sleep(10)
    rb.update()
    time.sleep(10)
    rb.check_status(sys.argv[2])
if __name__ == '__main__':
    main()
