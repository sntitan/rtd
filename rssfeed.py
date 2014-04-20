#!/usr/bin/python
from bencode import bdecode
import urllib2

def GetNameByDecodeFile(prefix, feedbuff):
    try:
        tor = bdecode(feedbuff)
    except:
        print("Invalid feed file.")
        return None
    if not tor.has_key('info'):
        return None
    if type(tor['info']) != type({}):
        return None
    if not tor['info'].has_key('name'):
        return None
    if type(tor['info']['name']) != type('str'):
        return None
    return '[' + prefix + ']'  + ' ' + tor['info']['name'] + '.torrent'

def DownloadTorrent(prefix, url):
    try:
        furl = urllib2.urlopen(url)
    except:
        print("URLError %s" % url)
        return
    feed = furl.read()
    furl.close()
    name = GetNameByDecodeFile(prefix, fhead)
    if name == None:
        print("Invalid addr maybe")
        return
    with open(name,"wb") as file:
        file.write(feed)


#test
DownloadTorrent('[TTG]', 'http://aaa')
#f = open('feed_test.torrent','rb')
#fb = f.read()
#f.close()
#name = GetNameByDecodeFile('[TTG]', fb)
#print name
