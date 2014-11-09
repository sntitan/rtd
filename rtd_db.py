#!/usr/bin/python
# coding=utf-8
import sqlite3

class rdbError(Exception):
    def __init__(self, errstr):
        self.value = errstr
    def __str__(self):
        return self.value

class torrent(object):
    def __init__(self, address):
        self.address = address
        self.file_name = None
        self.file_down_count = 0
        self.file_sha1 = None
        self.add_time = None

class rss_db(object):
    def open(self, db_name):
        self.db = sqlite3.connect(db_name)
    def close(self):
        self.db.close()
    def __init__(self, db_name):
        return self.open(db_name)
    def __del__(self):
        return self.close()
    def create_table(self, name):
        if self.is_table_exist(name):
            raise rdbError('Table %s is exists'%name)
        self.db.execute("CREATE TABLE IF NOT EXISTS %s \
                        (address TEXT NOT NULL, \
                        file_name TEXT NOT NULL, \
                        file_down_count INTERGER DEFAULT 1, \
                        sha1 TEXT NOT NULL, \
                        add_time DATETIME);" % name)

        pass
    def get_table_list(self):
        sor = self.db.cursor()
        tb_list = sor.execute("SELECT name FROM sqlite_master \
                               WHERE type='table'").fetchall()
        name_list = []
        for tname in tb_list:
            name_list.append(tname[0])
        return name_list
    def is_table_exist(self, name):
        namelist = self.get_table_list()
        for tname in namelist:
            if tname == name:
                return True
        return False
    def is_exist(self, key, value, web_name=None):
        if web_name:
            if not self.is_table_exist(web_name):
                raise rdbError('Table %s is not exists'% web_name)
            sor = self.db.cursor()
            sor.execute("SELECT * FROM %s \
                         WHERE %s='%s'" % \
                         (web_name, key, value))
            if len(sor.fetchall()) == 0:
                return False
            return True
        else:
            web_list = self.get_table_list()
            for web in web_list:
                if self.is_exist(key, value, web):
                    return True
            return False
    def is_addr_exist(self, addr, web_name=None):
        return self.is_exist('address', addr, web_name)
    def is_sha_exist(self, sha1, web_name=None):
        return self.is_exist('sha1', sha1, web_name)
    def add_tor(self, web, tor):
        if not self.is_table_exist(web):
            raise rdbError('Table %s is exists'%name)
        if self.is_addr_exist(tor.address, web):
            raise rdbError('Torrent[%s] address[%s] is exists'\
                          %(tor.file_name, tor.address))
        if self.is_sha_exist(tor.file_sha1, web):
            raise rdbError('Torrent[%s] sha1[%s] is exists'\
                          %(tor.file_name, tor.file_sha1))
        cmd = "INSERT INTO %s(address, file_name, sha1)\
               VALUES (?,?,?);" % web
        self.db.execute(cmd, (tor.address, tor.file_name, tor.file_sha1))
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
    rd.create_table('SN1')
    rd.create_table('SN2')
    assert rd.is_table_exist('SN1')
    assert rd.is_table_exist('SN2')
    assert rd.is_table_exist('SN3') == False

    #case2
    ccnt+=1
    t1 = torrent('address_torrent1')
    t1.file_name = 'name_t1'
    t1.file_down_count = 1
    t1.file_sha1 = 'abcdefgt1'
    rd.add_tor('SN1', t1)
    assert rd.is_addr_exist('address_torrent1')
    assert rd.is_addr_exist('address_torrent1', 'SN1')
    assert rd.is_addr_exist('address_torrent1', 'SN2') == False
    try:
        assert rd.is_addr_exist('address_torrent1', 'SN3') ==False
    except rdbError:
        pass
    else:
        assert False
    assert rd.is_sha_exist('abcdefgt1')
    assert rd.is_sha_exist('abcdefgt1', 'SN1')
    assert rd.is_sha_exist('abcdefgt1', 'SN2') == False
    try:
        assert rd.is_sha_exist('abcdefgt1', 'SN3') == False
    except rdbError:
        pass
    else:
        assert False

    #case3
    ccnt+=1
    t2 = torrent('address_torrent2')
    t2.file_name = 'name_t2'
    t2.file_down_count = 1
    t2.file_sha1 = 'abcdefgt2'
    rd.add_tor('SN2', t2)
    try:
        rd.add_tor('SN2', t2)
    except rdbError:
        pass
    else:
        assert False
    assert rd.is_addr_exist('address_torrent2')
    assert rd.is_addr_exist('address_torrent2', 'SN1') == False
    assert rd.is_addr_exist('address_torrent2', 'SN2') 
    assert rd.is_sha_exist('abcdefgt2')
    assert rd.is_sha_exist('abcdefgt2', 'SN1') == False
    assert rd.is_sha_exist('abcdefgt2', 'SN2')

    #case4
    ccnt+=1
    assert rd.is_addr_exist('address_torrent3') == False
    assert rd.is_sha_exist('abcdadfasdfsadfasfasdf') == False

    print 'All test finished, total num %u' % ccnt
    rd.close()
    os.remove(db_name)
