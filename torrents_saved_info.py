#!/usr/bin/python
import sqlite3
import time

def create_table(conn, name):
    sor = conn.cursor()
    create_sql = "CREATE TABLE IF NOT EXISTS " + name
    create_sql += " (addr TEXT, fname TEXT, dcnt INT, dtime TIMESTAMP, fsha1 TEXT)"
    sor.execute(create_sql)

def is_table_exists(sor, name):
    tb_list = sor.execute("select name from sqlite_master where type = 'table'").fetchall()
    for tname in tb_list:
        if tname[0] == name:
            return True
    return False

def find_torrent_by_addr(conn, name, addr):
    sor = conn.cursor()
    find_sql = "SELECT * FROM "+name+" WHERE addr='"+addr+"'"
    sor.execute(find_sql)
    return sor.fetchall()

def find_torrent_by_name(conn, host_name, torrent_name):
    sor = conn.cursor()
    find_sql = "SELECT * FROM "+name+" WHERE namer='"+name+"'"
    sor.execute(find_sql)
    return sor.fetchall()

def insert_torrent(conn, name, info):
    sor=conn.cursor()
    insert_sql="INSERT INTO "+name+" VALUES (?,?,?,?,?)"
    sor.execute(insert_sql,info)




#unit test
conn = sqlite3.connect("tmp.db")
###INIT
#create_table(conn,"ttg")
#insert_torrent(conn,'ttg',['http://ttg.im/test1','mame.test1',1,time.strftime('%Y-%m-%d %X', time.localtime()),'sha1 test1'])
#insert_torrent(conn,'ttg',['http://ttg.im/test2','mame.test2',1,time.strftime('%Y-%m-%d %X', time.localtime()),'sha1 test2'])
#insert_torrent(conn,'ttg',['http://ttg.im/test3','mame.test3',1,time.strftime('%Y-%m-%d %X', time.localtime()),'sha1 test3'])
#insert_torrent(conn,'ttg',['http://ttg.im/test4','mame.test4',1,time.strftime('%Y-%m-%d %X', time.localtime()),'sha1 test4'])
#create_table(conn,"chd")

#sor = conn.cursor()
#print is_table_exists(sor,'ttg')
#print is_table_exists(sor,'chd')
#print is_table_exists(sor,'ttg1')
conn.close()
