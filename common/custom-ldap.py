#!/usr/bin/python 
# -*- coding: UTF-8 -*-
import ldap

class zhe800Ldap(object):
    def __init__(self,url):
        self.url = url
        self.server = ldap.initialize(self.url)
    def search_info(self,baseDN,searchFilter,retrieveAttributes):
        result = self.server.search_s(baseDN,ldap.SCOPE_SUBTREE,searchFilter,retrieveAttributes)
        return result
