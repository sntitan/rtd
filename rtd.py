#!/usr/bin/python
# coding=utf-8
from rtd_conf import *
from rtd_db import *
import os
import hashlib
import feedparser
import urllib
import urllib2
from bencode import bdecode
import logging
import re
'''
TODO LIST
===
1. 修改下载流程，下载失败时，写入数据库，down_count为0
2. 读取rss网站之前，首先读取数据库中down_count为0的文件，尝试下载
3. 定时检查download目录是否有新文件出现，如果有新文件出现则更新到数据库中
4. 目前的下载方式urlretrieve貌似不能设置超时时间，需要找一个可以设置超时时间的方式
'''

g_tmp_tname = 'torrent.tmp'
g_logname = 'logfile/rtd.log'

def log_out(msg):
    logging.info(msg)
def debug_out(msg):
    logging.debug(msg)

def get_name_by_tfile(feedbuff):
    try:
        tor = bdecode(feedbuff)
    except:
        return None
    if not tor.has_key('info'):
        return None
    if type(tor['info']) != type({}):
        return None
    if not tor['info'].has_key('name'):
        return None
    if type(tor['info']['name']) != type('str'):
        return None
    return tor['info']['name']

def download_torrent(tor, path):
    if os.path.isfile(path):
        os.remove(path)
    try:
        urllib.urlretrieve(tor.address,path)
    except Exception, e:
        log_out("Download torrent err, addr %s" %tor.address)
        return None
    with open(path, 'r') as pf:
        buf = pf.read()
        tor.file_sha1 = hashlib.sha256(buf).hexdigest()
        tor.tor_name = get_name_by_tfile(buf)
    if not tor.tor_name:
        log_out('Invalid log file, addr %s'%tor.address)
        return None
    tor.file_name = tor.get_std_name()
    tor.file_down_count = tor.file_down_count + 1
    return True

def download_torrents_failed_last(db):
    pass

def mv_torrent(web, tor):
    with open(os.path.join(web.download_dir, tor.get_std_name()), 'wb') as wpf:
        with open(os.path.join(web.temp_download_dir, g_tmp_tname), 'rb') as rpf:
            wpf.write(rpf.read())

def save_undown_torrent(tor,db):
    pass

def get_all_addrs(web_addr):
    rss_web = feedparser.parse(web_addr)
    down_links = []
    for rss_tor in rss_web.entries:
        if not rss_tor.has_key('links'):
            log_out('Invalid rss-address[%s], cannot find links element'\
                     % web_addr)
            continue
        for addr_info in rss_tor['links']:
            if not addr_info.has_key('href'):
                log_out('Invalid rss-address[%s], cannot find href element'\
                         % web_addr)
                continue
            down_links.append(addr_info['href'])
    return down_links

def is_download_link(addr):
    conn = urllib2.urlopen(addr)
    cinfo = conn.info()
    conn.close()
    if not cinfo.has_key('content-type'):
        return False
    if cinfo['content-type'] == 'application/x-bittorrent':
        return True
    if not re.compile('torrent').search(cinfo['content-type']):
        return False
    log_out('Unknown content-type(%s) but i guess it is a torrent addr' % \
            cinfo['content-type'])
    return True

if __name__ == '__main__':
    #0. init resources
    g_name = 'rtd.ini'#stub
    rconf = rss_conf(g_name)
    rdb = rss_db(rconf.dbname)
    logging.basicConfig(filename=g_logname, 
                        level=logging.DEBUG, 
                        format='%(asctime)s %(levelname)s %(message)s',
                        encoding="UTF-8")
    
    #1. download the torrents which failed to downloaded last time
    download_torrents_failed_last(rdb)
    
    #2. read in rss and download torrents
    for rweb in rconf.webs:
        debug_out('Get torrents info from %s'%rweb.address)
        addrs = get_all_addrs(rweb.address)
        for tor_addr in addrs:
            #如果地址不是下载地址，则直接跳过，首先从数据库中查找，如果数据库中没有，再通过HEAD请求判断
            if rdb.is_webaddr_exist(tor_addr):
                debug_out('Not download link by db, addr %s'%tor_addr)
                continue
            if not is_download_link(tor_addr):
                debug_out('Not download link, addr %s'%tor_addr)
                rdb.add_webpage(webpage(tor_addr, rweb.name));
                continue
            #首先判断数据库中是否保存了种子地址，如果没保存，则开始下载
            if rdb.is_toraddr_exist(tor_addr):
                debug_out('Torrent address %s exists, skipped'%tor_addr)
                continue
            tor_name = os.path.join(rweb.temp_download_dir, g_tmp_tname)
            debug_out('Begin to download torrent, address %s, path %s'%\
                        (tor_addr, tor_name))
            tor = torrent(address = tor_addr, webname = rweb.name)
            if not download_torrent(tor, tor_name):
                #if failed to download the torrent, save to db and try to download it later
                log_out('failed to download torrent from address %s' % tor_addr)
                save_undown_torrent(tor, rdb)
                continue
            #下载完成后，应该立即写入数据库。
            #如果没有立即写入，后续的操作可能会continue，漏掉写入流程，
            #最终导致每次连接rss都会重复下载种子
            rdb.add_tor(tor)
            if rdb.is_sha_exist(tor.file_sha1):
                log_out('Duplicate torrent downloaded, addr[%s], name[%s]' \
                        % (tor.address, tor.file_name))
                continue 
            mv_torrent(rweb, tor)
            log_out('Download torrent[%s], from web[%s], address[%s]'\
                   % (tor.file_name, rweb.name, tor.address))
    
    #3. release all resources
    rdb.close()
