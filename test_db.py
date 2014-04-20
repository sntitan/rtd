#!/usr/bin/python
from torrents_saved_info import *

#unit test
conn = sqlite3.connect("tmp.db")
##INIT
#create_table(conn,"ttg")
#insert_torrent(conn,'ttg',['http://ttg.im/test1','mame.test1',1,time.strftime('%Y-%m-%d %X', time.localtime()),'sha1 test1'])
#insert_torrent(conn,'ttg',['http://ttg.im/test2','mame.test2',1,time.strftime('%Y-%m-%d %X', time.localtime()),'sha1 test2'])
#insert_torrent(conn,'ttg',['http://ttg.im/test3','mame.test3',1,time.strftime('%Y-%m-%d %X', time.localtime()),'sha1 test3'])
#insert_torrent(conn,'ttg',['http://ttg.im/test4','mame.test4',1,time.strftime('%Y-%m-%d %X', time.localtime()),'sha1 test4'])
#create_table(conn,"chd")
#
sor = conn.cursor()
print is_table_exists(sor,'ttg')
print is_table_exists(sor,'chd')
print is_table_exists(sor,'ttg1')
print find_torrent_by_addr(conn, 'ttg', 'http://ttg.im/test4')
print find_torrent_by_addr(conn, 'ttg', 'http://ttg.im/test5')
print find_torrent_by_addr(conn, 'ttg1', 'http://ttg.im/test5')
print find_torrent_by_name(conn, 'ttg', 'mame.test1')
print find_torrent_by_name(conn, 'ttg', 'name.test2')
conn.close()
