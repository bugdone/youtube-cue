import sys
import json
import subprocess
import re

import musicbrainz


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
    matches = [(t, re.match('0?%d+[ \./"-]* ?(.*)' % i, t['title'])) for (i, t) in enumerate(tracks, 1)]
    if all([m[1] for m in matches]):
        for (track, match) in matches:
            track['title'] = match.group(1).strip('"/-')
    return tracks


def guess_artist_album(d):
    t = d['title']
    t = re.sub('\(.*\)', '', t)
    t = re.sub('\[.*\]', '', t)
    t = re.sub('\{.*\}', '', t)
    t = t.strip()
    m = re.match('(.*)\s* -\s* (.*)', t)
    if m:
        d['artist'] = m.group(1)
        d['album'] = m.group(2)


def get_cue(url):
    o = subprocess.check_output(('youtube-dl -j ' + url).split())
    o = json.loads(o)
    title = o['fulltitle']
    d = dict(url=o['webpage_url'],
             duration=o['duration'],
             title=title,
             tracks=parse_description(o['description'], o['duration']))
    if d['tracks']:
        guess_artist_album(d)
        if d.get('artist'):
            musicbrainz.guess_tracks(d)
    return d
