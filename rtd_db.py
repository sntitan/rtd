#!/usr/bin/python
# coding=utf-8
import sqlite3
'''
TODO LIST
===
1. 将torrent类扩充，接受buffer作为参数，如果传入了buffer，则解析出文件名、sha1
2. torrent类添加获取标准种子名的方法，格式为 [网站名] 种子名.torrent
3. 修改add_tor方法，支持写入down_count次数
'''

torrents_table_name='torrents'

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

class rss_db(object):
    def open(self, db_name):
        self.db = sqlite3.connect(db_name)
        self.db.text_factory = str
        if not self.is_table_exist(torrents_table_name):
            self.create_torrents_table()
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

    def is_table_exist(self, name):
        sor = self.db.cursor()
        tb_list = sor.execute("SELECT name FROM sqlite_master \
                               WHERE type='table'").fetchall()
        for tname in tb_list:
            if tname[0] == name:
                return True
        return False
    def is_exist(self, key, value):
        sor = self.db.cursor()
        sor.execute("SELECT * FROM %s WHERE %s=?" % (torrents_table_name, key), 
                    (value,))
        all_found = sor.fetchall()
        if len(all_found) == 0:
            return None
        return all_found
    def is_addr_exist(self, addr):
        assert addr
        tors = self.is_exist('address', addr)
        if not tors:
            return False
        if len(tors) > 1:
            raise rdbError('Multiple addr %s in talbe' % addr)
        return True
    def is_sha_exist(self, sha1):
        assert sha1
        tors = self.is_exist('sha1', sha1)
        if not tors:
            return False
        return True
    def add_tor(self, tor):
        if tor.address:
            if self.is_addr_exist(tor.address):
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

    def update_addr_by_sha(self, tor):
        if not self.is_table_exist(torrents_table_name):
            raise rdbError('Table %s is exists'%torrents_table_name)
        if not self.is_sha_exist(tor.file_sha1):
            raise rdbError("Torrent's sha1[%s] is not exists" % tor.file_sha1)
        self.db.execute("UPDATE %s SET address=? WHERE sha1=?"%torrents_table_name,\
                        (tor.address, tor.file_sha1))
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
    assert rd.is_addr_exist('address_torrent2')
    assert rd.is_sha_exist('abcdefgt2')

    #case4
    ccnt+=1
    assert rd.is_addr_exist('address_torrent3') == False
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
    t4 = torrent()
    t4.web_name = 'SN3'
    t4.address = 'address_torrent4_before'
    t4.file_name = 'name_t4'
    t4.file_sha1 = 'abcdefgt4'
    rd.add_tor(t4)
    assert rd.is_sha_exist('abcdefgt4')
    assert rd.is_addr_exist('address_torrent4_before')
    assert rd.is_addr_exist('address_torrent4_after') == False
    t4.address = 'address_torrent4_after'
    rd.update_addr_by_sha(t4)
    assert rd.is_addr_exist('address_torrent4_before') == False
    assert rd.is_addr_exist('address_torrent4_after')

    #case7
    try:
        rd.is_addr_exist(None)
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

    print 'All test finished, total num %u' % ccnt
    rd.close()
    os.remove(db_name)
