from __future__ import print_function

import requests
import re
import os.path
import pickle
import mutagen
from mutagen.easyid3 import EasyID3

# you may want to edit these
dbfilename = "bucket.p"
dirpath = os.path.dirname(os.path.realpath(__file__))
trackdir = dirpath + '/tracks'
dbfilepath = dirpath + '/' + dbfilename


# a dictionary of tracks to avoid dups
def open_map():
    if (os.path.isfile(dbfilepath)):
        return pickle.load(open(dbfilepath, "r"))
    else:
        return {}


def close_map(m):
    pickle.dump(m, open(dbfilepath, "w+"))


# sessions
def open_session(url):
    s = requests.Session()
    s.get(url)
    return s


def close_session(s):
    s.close()


# generic track information
def get_track_url(song_page_url, s):
    r = s.get(song_page_url)
    if (r.status_code == 200):
        key = re.findall('"key":"[0-9a-f]+"', r.text)[0]
        key = key.split('"')[-2]
        itemid = song_page_url.split('/')[4]
        # or re.findall('"page_arg":"[a-z0-9]+"', page.text)[0]
    else:
        # could be something else
        print("couldn't get the songs page on hypem")
        return None
    r = s.get('http://hypem.com/serve/source/%s/%s' % (itemid, key))
    if (r.status_code == 200):
        return r.json()["url"]
    else:
        # could be something else
        print("couldn't get the songs source page. it contains the" +
              " streaming link. this may be a cookie issue")
        return None


def get_feed_tracks(feed_url, s):
    r = requests.get(feed_url)
    if (r.status_code == 200):
        titles = re.findall('<title>.*</title>', r.text)
        links = re.findall('<link>.*</link>', r.text)
        # prolly a better way to do this. eh
        titles = map(lambda (x): x.split('>')[1].split('<')[0], titles)[1:]
        links = map(lambda (x): x.split('>')[1].split('<')[0], links)[1:]
        links = map(lambda (x): get_track_url(x, s), links)
        return zip(titles, links)
    else:
        return None


# global tracks
def get_top_20():
    m = open_map()
    s = open_session('http://hypem.com/')
    top20 = get_feed_tracks('http://hypem.com/feed/popular/3day/1/feed.json', s)
    download_list(top20, m)
    close_session(s)
    close_map(m)


# user tracks
def get_user_love_pages(usr, s):
    i = 1
    res = []
    while (True):
        url = 'http://hypem.com/feed/loved/%s/%s/feed.json' % (usr, str(i))
        loves = get_feed_tracks(url, s)
        if (loves):
            res += loves
            i += 1
        else:
            return res


def get_loves(usr):
    m = open_map()
    s = open_session('http://hypem.com/%s' % usr)
    loves = get_user_love_pages(usr, s)
    download_list(loves, m)
    close_session(s)
    close_map(m)


# downloading
# assumes tuples like (name, url)
def download_list(ls, m):
    for elm in ls:
        if (elm[1]):
            # remove slashes that are space-padded
            filename = re.sub('[ / ]', '-', elm[0])
            # remove parens
            re.sub('[()]', '', filename)
            # replace muliple '-' with one
            filename = re.sub('[-]+', '-', filename)
            download_track(elm[1], elm[0], trackdir + '/'
                           + filename + ".mp3", m)


def download_track(url, track, filepath, m):
    if (track not in m):
        print("%s wasn't found. we'll download that jam for you", track)
        download_from_stream(requests.get(url, stream=True), filepath)
        # let's add some tags
        if os.path.isfile(filepath):
            # just in case there are two ' - ' join on title
            # there could be cases where this messes up the
            # artist name
            t = re.split(' - ', track)
            artist = t[0]
            title = ' - '.join(t[1:])
            try:
                meta = EasyID3(filepath)
            except mutagen.id3.ID3NoHeaderError:
                meta = mutagen.File(filepath, easy=True)
                meta.add_tags()
            meta['title'] = title
            meta['artist'] = artist
            meta.save()
            m[track] = 1
        else:
            print("we tried to add the metadata but" +
                  "it appears the file is missing")
    else:
        print("oh hey %s was found. you should already be enjoying it" % track)
        m[track] += 1


def download_from_stream(strm_req, filename):
    if (os.path.exists(filename)):
        print('%s already exists, skipping' % (filename))
        return 1

    f = open(filename, 'w')
    filesize = strm_req.headers['content-length']
    for chunk in strm_req.iter_content(chunk_size=1024):
        if chunk:
            f.write(chunk)
        else:
            print('error w/ %s' % (filename))
            return 2
    print('dl complete - %s - %s' % (filesize, filename))
    f.close()
