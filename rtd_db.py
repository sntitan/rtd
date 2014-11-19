#!/usr/bin/python
# coding=utf-8
import sqlite3
'''
TODO LIST
===
1. 将torrent类扩充，接受buffer作为参数，如果传入了buffer，则解析出文件名、sha1
'''

torrents_table_name='torrents'
webpage_table_name='webpage'

class rdbError(Exception):
    def __init__(self, errstr):
        self.value = errstr
    def __str__(self):
        return self.value

class torrent(object):
    def __init__(self, address=None, webname=None):
        self.web_name = webname
        self.address = address
        self.tor_name = None
        self.file_name = None
        self.file_down_count = 0
        self.file_sha1 = None
        self.add_time = None
    def get_std_name(self):
        if not self.file_name:
            assert self.tor_name
            assert self.web_name
            self.file_name = '[%s] %s.torrent' % (self.web_name, self.tor.name)
        return tor.file_name

class webpage(object):
    def __init__(self, address, webname):
        self.web_name = webname
        self.address = address

class rss_db(object):
    def open(self, db_name):
        self.db = sqlite3.connect(db_name)
        self.db.text_factory = str
        if not self.is_table_exist(torrents_table_name):
            self.create_torrents_table()
        if not self.is_table_exist(webpage_table_name):
            self.create_webpage_table()
    def close(self):
        self.db.close()
    def __init__(self, db_name):
        self.open(db_name)
    def __del__(self):
        return self.close()
    def create_torrents_table(self):
        if self.is_table_exist(torrents_table_name):
            raise rdbError('Table %s is exists'%torrents_table_name)
        self.db.execute("CREATE TABLE IF NOT EXISTS %s \
                        (web_name TEXT NOT NULL, \
                        address TEXT, \
                        file_name TEXT NOT NULL, \
                        file_down_count INTERGER DEFAULT 1, \
                        sha1 TEXT NOT NULL, \
                        add_time DATETIME);" % torrents_table_name)
    def create_webpage_table(self):
        if self.is_table_exist(webpage_table_name):
            raise rdbError('Table %s is exists'%webpage_table_name)
        self.db.execute("CREATE TABLE IF NOT EXISTS %s \
                        (web_name TEXT, address TEXT NOT NULL);" % webpage_table_name)
    def is_table_exist(self, name):
        sor = self.db.cursor()
        tb_list = sor.execute("SELECT name FROM sqlite_master \
                               WHERE type='table'").fetchall()
        for tname in tb_list:
            if tname[0] == name:
                return True
        return False
    def is_exist(self, table_name, key, value):
        sor = self.db.cursor()
        sor.execute("SELECT * FROM %s WHERE %s=?" % (table_name, key), 
                    (value,))
        all_found = sor.fetchall()
        if len(all_found) == 0:
            return None
        return all_found
    def is_exist_single(self, table_name, key, value):
        assert key
        assert value
        tors = self.is_exist(table_name, key, value)
        if not tors:
            return False
        if len(tors) > 1:
            raise rdbError('Multiple key/value %s/%s in talbe' % (key,value))
        return True
    def is_toraddr_exist(self, addr):
        return self.is_exist_single(torrents_table_name, 'address', addr)
    def is_webaddr_exist(self, addr):
        return self.is_exist_single(webpage_table_name, 'address', addr)
    def is_addr_exist(self, addr):
        if self.is_toraddr_exist(addr):
            return True
        if self.is_webaddr_exist(addr):
            return True
        return False
    def is_sha_exist(self, sha1):
        assert sha1
        tors = self.is_exist(torrents_table_name, 'sha1', sha1)
        if not tors:
            return False
        return True

    def add_tor(self, tor):
        if tor.address:
            if self.is_toraddr_exist(tor.address):
                raise rdbError('Torrent[%s] address[%s] is exists'\
                              %(tor.file_name, tor.address))
            self.db.execute("INSERT INTO %s(web_name, address, file_name, file_down_count, sha1) \
                VALUES (?,?,?,?,?)" % torrents_table_name, 
                (tor.web_name, tor.address, tor.file_name, tor.file_down_count, tor.file_sha1))
        else:
            self.db.execute("INSERT INTO %s(web_name, file_name, file_down_count, sha1) \
                            VALUES (?,?,?,?)" % torrents_table_name, 
                            (tor.web_name, tor.file_name, tor.file_down_count, tor.file_sha1))
        self.db.commit()

    def set_toraddr_by_sha(self, tor):
        if not self.is_table_exist(torrents_table_name):
            raise rdbError('Table %s is exists'%torrents_table_name)
        if not self.is_sha_exist(tor.file_sha1):
            raise rdbError("Torrent's sha1[%s] is not exists" % tor.file_sha1)
        self.db.execute("UPDATE %s SET address=? WHERE sha1=?"%torrents_table_name,\
                        (tor.address, tor.file_sha1))
        self.db.commit()

    def get_downcnt0_list(self):
        sor = self.db.cursor()
        sor.execute("SELECT address FROM %s WHERE file_down_count=0" % torrents_table_name)
        addr_list_db = sor.fetchall()
        addr_list = []
        for addr_db in addr_list_db:
            addr_list.append(addr_db[0])
        return addr_list
    def set_downcnt(self, addr, downcnt):
        self.db.execute("UPDATE %s SET file_down_count=? WHERE address=?"%\
                        torrents_table_name, (downcnt, addr))
        self.db.commit()

    def add_webpage(self, web):
        if self.is_webaddr_exist(web.address):
            raise rdbError('webpage address[%s] is exists'%web.address)
        self.db.execute("INSERT INTO %s(web_name, address) VALUES (?,?)"%webpage_table_name,\
                        (web.web_name, web.address))
        self.db.commit()

if __name__ == '__main__':
    import os
    db_name = 'test.db'
    print 'debug mode...'
    if os.path.isfile(db_name):
        os.remove(db_name)
    rd = rss_db(db_name)
    #test case begin
    print 'begin and test all...'
    ccnt = 0
    #case1
    ccnt+=1
    assert rd.is_table_exist(torrents_table_name)
    assert rd.is_table_exist('SN3') == False

    #case2
    ccnt+=1
    t1 = torrent()
    t1.web_name = 'SN1'
    t1.address = None
    t1.file_name = 'name_t1'
    t1.file_down_count = 1
    t1.file_sha1 = 'abcdefgt1'
    rd.add_tor(t1)
    assert rd.is_sha_exist('abcdefgt1')

    #case3
    ccnt+=1
    t2 = torrent()
    t2.web_name = 'SN2'
    t2.address = 'address_torrent2'
    t2.file_name = 'name_t2'
    t2.file_down_count = 1
    t2.file_sha1 = 'abcdefgt2'
    rd.add_tor(t2)
    try:
        rd.add_tor(t2)
    except rdbError as e:
        pass
    else:
        assert False
    assert rd.is_toraddr_exist('address_torrent2')
    assert rd.is_addr_exist('address_torrent2')
    assert rd.is_webaddr_exist('address_torrent2') == False
    assert rd.is_sha_exist('abcdefgt2')

    #case4
    ccnt+=1
    assert rd.is_toraddr_exist('address_torrent3') == False
    assert rd.is_addr_exist('address_torrent3') == False
    assert rd.is_webaddr_exist('address_torrent3') == False
    assert rd.is_sha_exist('abcdadfasdfsadfasfasdf') == False

    #case5
    from rtd import get_name_by_tfile
    ccnt+=1
    t3 = torrent()
    t3.web_name = 'SN3'
    t3.address = 'address_torrent3'
    with open('debian-7.6.0-amd64-DVD-1.iso.torrent', 'rb') as pf:
        t3.file_name = get_name_by_tfile(pf.read())
    t3.file_down_count = 1
    t3.file_sha1 = 'abcdefgt3'
    rd.add_tor(t3)

    #case6
    ccnt+=1
    t4 = torrent()
    t4.web_name = 'SN3'
    t4.address = 'address_torrent4_before'
    t4.file_name = 'name_t4'
    t4.file_sha1 = 'abcdefgt4'
    t4.file_down_count = 1
    rd.add_tor(t4)
    assert rd.is_sha_exist('abcdefgt4')
    assert rd.is_toraddr_exist('address_torrent4_before')
    assert rd.is_toraddr_exist('address_torrent4_after') == False
    t4.address = 'address_torrent4_after'
    rd.set_toraddr_by_sha(t4)
    assert rd.is_toraddr_exist('address_torrent4_before') == False
    assert rd.is_toraddr_exist('address_torrent4_after')

    #case7
    ccnt+=1
    try:
        rd.is_toraddr_exist(None)
    except AssertionError:
        pass
    else:
        assert False
    try:
        rd.is_sha_exist(None)
    except AssertionError:
        pass
    else:
        assert False

    #case8
    ccnt+=1
    wp = webpage('webpage_address1', 'SN1')
    rd.add_webpage(wp)
    assert rd.is_webaddr_exist('webpage_address1')
    assert rd.is_addr_exist('webpage_address1')
    assert rd.is_toraddr_exist('webpage_address1') == False
    
    #case9
    ccnt+=1
    t5 = torrent()
    t5.web_name = 'SN3'
    t5.address = 'address_torrent5_before'
    t5.file_name = 'name_t5'
    t5.file_sha1 = 'abcdefgt5'
    t5.file_down_count = 0
    rd.add_tor(t5)
    t6 = torrent()
    t6.web_name = 'SN3'
    t6.address = 'address_torrent6_before'
    t6.file_name = 'name_t6'
    t6.file_sha1 = 'abcdefgt6'
    t6.file_down_count = 0
    rd.add_tor(t6)
    addr_list = rd.get_downcnt0_list()
    assert len(addr_list) == 2
    assert addr_list[0] == 'address_torrent5_before'
    assert addr_list[1] == 'address_torrent6_before'
    rd.set_downcnt(addr_list[0], 1)
    rd.set_downcnt(addr_list[1], 2)
    addr_list = rd.get_downcnt0_list()
    assert len(addr_list) == 0

    print 'All test finished, total num %u' % ccnt
    rd.close()
    os.remove(db_name)
