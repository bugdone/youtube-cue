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


def parse_description(description):
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
    # If track no is present, remove lines without it
    matches = [(t, re.match('\s*0?%d+[ ./"-]* ?(.*)' % i, t['title'])) for (i, t) in enumerate(tracks, 1)]
    if len([1 for m in matches if m[1]]) >= len(tracks) / 2:
        tracks = []
        for (track, match) in matches:
            if match:
                tracks.append(track)
                tracks[-1]['title'] = match.group(1)
    if tracks != sorted(tracks, key=lambda x: x['offset']):
        # Got track lengths, not offsets
        lengths = [0] + [t['offset'] for t in tracks]
        for i in range(len(tracks)):
            tracks[i]['offset'] = lengths[i] + (tracks[i - 1]['offset'] if i > 0 else 0)
    for track in tracks:
        track['title'] = track['title'].strip('"/- \t')
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


def add_duration(tracks, duration):
    for i in range(len(tracks) - 1):
        tracks[i]['duration'] = tracks[i + 1]['offset'] - tracks[i]['offset']
    tracks[-1]['duration'] = duration - tracks[-1]['offset']


def get_cue(url):
    log('id', youtube.get_youtube_id(url))
    o = subprocess.check_output(('youtube-dl -j ' + url).split())
    o = json.loads(o)
    title = o['fulltitle']
    log('youtubedl', {k: v for (k, v) in o.iteritems() if k in ('fulltitle', 'duration', 'webpage_url', 'description')})
    d = dict(url=o['webpage_url'],
             duration=o['duration'],
             title=title,
             tracks=parse_description(o['description']))
    log('parsed_description', d['tracks'])
    if not d['tracks']:
        comments = list(youtube.get_comments(d['url']))
        log('comments', comments)
        for comment in comments:
            d['tracks'] = parse_description(comment)
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
        add_duration(d['tracks'], d['duration'])
    if log_path:
        log('output', d)
        write_log()
    return d
