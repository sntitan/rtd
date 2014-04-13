#!/usr/bin/python
import sys
import sqlite3
import time
import ConfigParser

###config
config_file_name='tord.ini'
db_file_name='tord.db'

def out_debug(str):
    print("[DEBUG]%s"%str)

def out_error(str):
    print("[ERROR]%s"%str)

def out_info(str):
    print("[INFO]%s"%str)

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
#conn = sqlite3.connect("tmp.db")
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
#conn.close()



#config file adapt
def is_setting_secname(secname):
    if secname == 'global':
        return True
    return False

def get_down_dirs(cfg):
    try:
        gi = cfg.items('global')
    except ConfigParser.NoSectionError:
        out_debug("Section global is not exists")
        return ('','')
    except:
        out_error("Unknown error occured")
	return ('','')

    down_dir = ''
    indown_dir = ''
    for item in gi:
        if item[0] == 'download-dir':
            down_dir = item[1]
        if item[0] == 'incomplete-dir':
            indown_dir = item[1]
    if indown_dir == '':
        indown_dir = down_dir
    return (down_dir, indown_dir)



#torrents analyser
def download_torrent(addr, save_dir):
    return 'sha1'

def download_all_torrents(rss_addr, down_dir):
    return

#1.Analyse argus
arg_num = len(sys.argv)
for i in range(1,arg_num):
    out_debug(sys.argv[i])

#2.Read in config file and init db
cfg = ConfigParser.SafeConfigParser()
out_debug("config file %s, read in"%config_file_name)
if len(cfg.read(config_file_name)) == 0:
    out_error("Config file %s is not exists"%config_file_name)
    exit(0)

#3.get directory where torrents to be downloaded
tdir = get_down_dirs(cfg)
if tdir[0] == '':
    out_error('A download-dir where torrents saved, should be specified')
    exit(0)
out_debug("Download dir '%s'"%tdir[0])
out_debug("Incomplete download dir '%s'"%tdir[1])

#4.Open database and init
out_debug("database file %s, open"%db_file_name)
tdb = sqlite3.connect(db_file_name)
for secname in cfg.sections():
    if is_setting_secname(secname):
        out_debug("section %s is a setting one, ignore"%secname)
        continue
    if is_table_exists(tdb, secname):
        out_debug("section %s exists"%secname)
        continue
    out_info("Init table %s"%secname)
    create_table(tdb, secname)

#5.download torrents one by one
for secname in cfg.sections():
    sec_items = cfg.items(secname)
    for item in sec_items:
        if (item[0] != 'addr'):
            continue
        if (item[1] == ''):
            out_error("Addr is empty in section %s"%secname)
            continue
        out_debug("Begin to download all torrents in section %s, addr '%s'"%(secname, item[1]))
        download_all_torrents(item[1], tdir)

tdb.close()
