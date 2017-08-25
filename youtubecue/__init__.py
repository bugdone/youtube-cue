import json
import os.path
import subprocess
import re

import musicbrainz
from musicbrainz import init_musicbrainz
import youtube

log_path = None
log_data = {}


def set_log_path(path):
    global log_path
    log_path = path


def log(key, value):
    if log_path:
        global log_data
        log_data[key] = value


def write_log():
    with open(os.path.join(log_path, log_data['id']), 'w') as f:
        json.dump(log_data, f, indent=4)


def get_offset(hours, minutes, seconds):
    return (int(hours) * 3600 if hours else 0) + int(minutes) * 60 + int(seconds)


def parse_description(description, duration):
    tracks = []
    for line in description.splitlines():
        m = re.search('(\(?\[?(?:(\d+):)?(\d+):(\d+))(?:.*)(?:(?:\d+:)?\d+:\d+)?', line)
        if m is None:
            continue
        if m.start(1) > len(line) - m.end(1):
            title = line[:m.start(1)]
        else:
            title = line[m.end(1):]
        title = title.strip()
        tracks.append(dict(title=title, offset=get_offset(m.group(2), m.group(3), m.group(4))))
        if len(tracks) > 1:
            tracks[-2]['duration'] = tracks[-1]['offset'] - tracks[-2]['offset']
    if tracks:
        tracks[-1]['duration'] = duration - tracks[-1]['offset']
    matches = [(t, re.match('\s*0?%d+[ \./"-]* ?(.*)' % i, t['title'])) for (i, t) in enumerate(tracks, 1)]
    if all([m[1] for m in matches]):
        for (track, match) in matches:
            track['title'] = match.group(1).strip('"/-')
    return tracks


def guess_artist_album(d):
    ignore = ['\(.*\)', '\[.*\]', '\{.*\}', 'full album.*', '(?<!\w)hd(?!\w)', '(?<!\w)hq(?!\w)']
    t = d['title']
    for regexp in ignore:
        t = re.sub(regexp, '', t, flags=re.IGNORECASE)
    t = t.strip()
    m = re.match('(.*)\s* -\s* (.*)', t)
    if m:
        d['artist'] = m.group(1)
        d['album'] = m.group(2)
        if len(d['album']) > 2 and d['album'].startswith('"') and d['album'].startswith('"'):
            d['album'] = d['album'].strip('"')


def get_cue(url):
    log('id', youtube.get_youtube_id(url))
    o = subprocess.check_output(('youtube-dl -j ' + url).split())
    o = json.loads(o)
    title = o['fulltitle']
    log('youtubedl', {k: v for (k, v) in o.iteritems() if k in ('fulltitle', 'duration', 'webpage_url', 'description')})
    d = dict(url=o['webpage_url'],
             duration=o['duration'],
             title=title,
             tracks=parse_description(o['description'], o['duration']))
    if not d['tracks']:
        comments = list(youtube.get_comments(d['url']))
        log('comments', comments)
        for comment in comments:
            d['tracks'] = parse_description(comment, d['duration'])
            if d['tracks']:
                log('comment', comment)
                break
    if len(d['tracks']) < 2:
        # Not much of a cue with just 1 track, eh?
        d['tracks'] = []
    if d['tracks']:
        guess_artist_album(d)
        if d.get('artist'):
            musicbrainz.guess_tracks(d)
    if log_path:
        log('output', d)
        write_log()
    return d
