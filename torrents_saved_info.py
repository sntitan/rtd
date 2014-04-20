#!/usr/bin/python
import sys
import sqlite3
import time
import ConfigParser
import feedparser
import urllib2
import hashlib
import os
import shutil

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
    if not is_table_exists(conn, name):
        return []
    sor = conn.cursor()
    find_sql = "SELECT * FROM "+name+" WHERE addr='"+addr+"'"
    sor.execute(find_sql)
    return sor.fetchall()

def find_torrent_by_name(conn, host_name, torrent_name):
    if not is_table_exists(conn, host_name):
        return []
    sor = conn.cursor()
    find_sql = "SELECT * FROM "+host_name+" WHERE fname='"+torrent_name+"'"
    sor.execute(find_sql)
    return sor.fetchall()

def find_torrent_by_hash(conn, host_name, torrent_hash):
    if not is_table_exists(conn, host_name):
        return []
    sor = conn.cursor()
    find_sql = "SELECT * FROM "+host_name+" WHERE fsha1='"+torrent_hash+"'"
    sor.execute(find_sql)
    return sor.fetchall()

def insert_torrent(conn, name, info):
    sor=conn.cursor()
    insert_sql="INSERT INTO "+name+" VALUES (?,?,?,?,?)"
    sor.execute(insert_sql,info)


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
def calc_sha1(filepath):
    with open(filepath,'rb') as f:
        sha1obj = hashlib.sha1()
        sha1obj.update(f.read())
        hash = sha1obj.hexdigest()
        return hash

def download_torrent(url, save_path):
    try:
        urllib.urlretrieve(url,save_path)
    except:
        out_err("Download torrent err, addr %s" % url)
        return None
    with open(save_path, 'r') as pf:
        return hashlib.sha256(f.read()).hexdigest()
    return None

    pf = open(down_full_path,'r')
    pbuff = pf.read()
    name = GetNameByDecodeFile(prefix,pbuff)
    if name == None:
        out_err("Invalid addr maybe")
        return
    with open(name,"wb") as file:
        file.write(feed)
    return 'sha1'

def download_torrents_list(db, host_name, addr_list, down_dir):
    for addr_info in addr_list:
        if not addr_info.has_key('href'):
            continue
        addr = addr_info['href']
        if len(find_torrent_by_addr(db, host_name, addr) != 0):
            continue
        tmp_torrent_path = os.path.join(down_dir[1],'torrent.tmp')
        if os.path.isfile(tmp_torrent_path):
            os.remove(tmp_torrent_path)
        tsha = download_torrent(addr,tmp_torrent_path)
        if (tsha == None):
            out_err('Download from addr %s fail'%addr)
            continue
        with open(tmp_torrent_path,'r') as f:
            tor_name = GetNameByDecodeFile(host_name, f.read())
        if tor_name == None:
            out_err("Invalid file format")
            continue
        if len(find_torrent_by_hash(db, host_name, tsha)) != 0:
            out_info('Download file %s but the same hash'%tor_name)
        else:
            out_info('Download file %s from addr %s'%(tor_name,addr))
            tor_path = os.path.join(down_dir[0],tor_name)
            shutil.move(tmp_torrent_path,tor_path)
            os.remove(tmp_torrent_path)
        insert_torrent(db, host_name,[(addr,tor_name,1,time.strftime('%Y-%m-%d %X', time.localtime()),tsha)])
    return

def download_all_torrents(db, host_name, rss_addr, down_dir):
    hd = feedparser.parse(rss_addr)
    for feed in hd.entries:
        if len(feed.enclosures != 0):
            download_torrents_list(db, host_name, feed.enclosures, down_dir)
        else:
            download_torrents_list(db, host_name, feed.links, down_dir)

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

#5.download torrents site by site
for secname in cfg.sections():
    sec_items = cfg.items(secname)
    for item in sec_items:
        if (item[0] != 'addr'):
            continue
        if (item[1] == ''):
            out_error("Addr is empty in section %s"%secname)
            continue
        out_debug("Begin to download all torrents in section %s, addr '%s'"%(secname, item[1]))
        download_all_torrents(tdb, secname, item[1], tdir)

tdb.close()
