#!/usr/bin/python
# coding=utf-8

class rss_web(object):
    def __init__(self, name, address, ddir, tddir=None):
        self.name = name
        self.address = address
        self.download_dir = ddir
        if tddir:
            self.temp_download_dir = tddir
        else:
            self.temp_download_dir = ddir

    def get_all_addrs(self):
        pass

class rss_conf(object):
    def read_in_conf(self, conf_name):
        pass
    def init_db(self):
        pass
    def __init__(self, conf_name):
        self.webs = []
        self.dbname = ''

