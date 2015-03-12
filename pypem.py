from __future__ import print_function

import requests
import re
import os

login_page = 'http://hypem.com/inc/lb_login.php'

def get_hype_session(user, password):
    payload = {'user_screen_name' : user,
               'user_password' : password}

    s = requests.session()
    s.post(login_page, data=payload)

    return s

def get_hype_url(song_page_url, s):
    r = s.get(song_page_url)
    if (r.status_code == 200):
        key = re.findall('"key":"[0-9a-f]+"', r.text)[0]
        key = key.split('"')[-2]
        itemid = song_page_url.split('/')[4]
        # or re.findall('"page_arg":"[a-z0-9]+"', page.text)[0]
    else:
        # could be something else
        print("Your cookies are stale")
        return None
    r = s.get('http://hypem.com/serve/source/%s/%s' % (itemid, key))
    if (r.status_code == 200):
        return r.json()["url"]
    else:
        # could be something else
        print("Your cookies are stale")
        return None

def get_hype_from_feed(feed_url, s):
    r = s.get(feed_url)
    if (r.status_code == 200):
        titles = re.findall('<title>.*</title>', r.text)
        links = re.findall('<link>.*</link>', r.text)
        # prolly a better way to do this. eh
        titles = map(lambda (x) : x.split('>')[1].split('<')[0], titles)[1:]
        links = map(lambda (x) : x.split('>')[1].split('<')[0], links)[1:]
        links = map(lambda (x) : get_hype_url(x, s), links)
        return zip(titles, links)
    else:
        return None

def get_hype_popular_last_3_days(s):
    return get_hype_from_feed('http://hypem.com/feed/popular/3day/1/feed.json', s)

def get_hype_user_loves(usr, s):
    i = 1
    res = []
    while (True):
        url = 'http://hypem.com/feed/loved/%s/%s/feed.json' % (usr, str(i))
        loves = get_hype_from_feed(url, s)
        if (loves):
            res += loves
            i += 1
        else:
            return res

# assumes tuples like (name, url)
def download_list(ls):
    for elm in ls:
        if (elm[1]):
            download_track(elm[1], elm[0] + ".mp3")

def download_track(url, name):
    download_file_from_stream(requests.get(url, stream=True), name)

def download_file_from_stream(strm_req, filename):
    if (os.path.exists(filename)):
        print('%s already exists, skipping' % (filename))
        return 1

    f = open(filename.replace('/', '_'), 'w')
    filesize = strm_req.headers['content-length']
    for chunk in strm_req.iter_content(chunk_size=1024):
        if chunk:
            f.write(chunk)
        else:
            print('error w/ %s' % (filename))
            return 2
    print('dl complete - %s - %s' % (filesize, filename))
    f.close()
