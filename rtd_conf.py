#!/usr/bin/python
# coding=utf-8
import ConfigParser

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
    def read_in_value(self, web_name, key):
        if not self.conp.has_option(web_name, key):
            return None
        return self.conp.get(web_name, key)
    def read_in_global(self):
        self.global_web = self.read_in_web('global', force_read=True)
        self.dbname = self.read_in_value('global', 'db_name')
    def read_in_web(self, web_name, force_read=False):
        web = rss_web(web_name, None, None, None)
        web.address = self.read_in_value(web_name, 'address')
        web.download_dir = self.read_in_value(web_name, 'download_dir')
        web.temp_download_dir = self.read_in_value(web_name, 'temp_download_dir')
        if not web.address and not force_read:
            return None
        if not web.download_dir:
            web.download_dir = self.global_web.download_dir
        if not web.temp_download_dir:
            web.temp_download_dir = self.global_web.temp_download_dir
        return web
            
    def read_in_conf(self, conf_name):
        self.conp = ConfigParser.SafeConfigParser()
        self.conp.read(conf_name)
        for sec in self.conp.sections():
            if sec == 'global':
                self.read_in_global()
            else:
                web = self.read_in_web(sec)
                if web:
                    self.webs.append(web)
    def __init__(self, conf_name):
        self.webs = []
        self.dbname = ''
        self.global_web = rss_web(None, None, None, None)
        self.read_in_conf(conf_name)

if __name__ == '__main__':
    fname = 'test.cfg'
    print 'Begin ut test...'
    rc = rss_conf(fname)

    assert rc.dbname == 'test1.db'
    assert rc.global_web.name == 'global'
    assert rc.global_web.address == None
    assert rc.global_web.download_dir == 'test'
    assert rc.global_web.temp_download_dir == 'test/temp'

    assert len(rc.webs) == 2
    assert rc.webs[0].name == 'SN1'
    assert rc.webs[0].address == 'http://sn1_address.com'
    assert rc.webs[0].download_dir == rc.global_web.download_dir
    assert rc.webs[0].temp_download_dir == rc.global_web.temp_download_dir

    assert rc.webs[1].name == 'SN2'
    assert rc.webs[1].address == 'http://sn2_address.com'
    assert rc.webs[1].download_dir == 'test_sn2'
    assert rc.webs[1].temp_download_dir == 'test_sn2/temp'
    print 'test end'
