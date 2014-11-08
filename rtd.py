#!/usr/bin/python
# coding=utf-8
from rtd_conf import *
from rtd_db import *

def log_out(msg):
    pass

class torrent(object):
    def __init__(self, address):
        self.address = address
        self.file_name = None
        self.file_down_count = 0
        self.file_sha1 = None
        self.add_time = None

def download_torrent(addr, path):
    pass

def save_torrent(tor, db):
    pass

g_name = '' #stub

rconf = rss_conf(g_name)
rdb = rss_db(rconf.dbname)
for rweb in rconf.webs:
    addrs = rweb.get_all_addrs()
    for tor_addr in addrs:
        if not rdb.is_addr_exist(tor_addr, rweb.name):
            continue
        tor = download_torrent(tor_addr, rweb.temp_download_dir)
        if not tor:
            log_out('failed to download torrent from address %s' % tor_addr)
            continue
        if rdb.is_sha_exist(tor.file_sha1):
            log_out('Duplicate torrent downloaded, addr[%s], name[%s]' \
                    % (tor.address, tor.file_name))
            continue
        save_torrent(tor, rdb)
        log_out('Download torrent[%s], from web[%s], address[%s]'\
               % (tor.file_name, rweb.name, tor.address))
