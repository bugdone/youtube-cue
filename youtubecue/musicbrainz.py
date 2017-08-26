import difflib
import logging
import pprint

import musicbrainzngs

import youtubecue


def init_musicbrainz(*args, **kwargs):
    musicbrainzngs.set_useragent(*args, **kwargs)


def get_tracks(artist, album):
    recordings = musicbrainzngs.search_recordings(artist=artist, release=album)['recording-list']
    youtubecue.log_data('musicbrainz', recordings)
    return [r['title'] for r in recordings]


def match_tracks(cue, mb_tracks):
    mb_tracks = set(mb_tracks)
    for track in cue['tracks']:
        if len(mb_tracks) == 0:
            return
        by_ratio = sorted([(t, difflib.SequenceMatcher(a=track['title'], b=t).ratio()) for t in mb_tracks],
                          key=lambda x: -x[1])
        if by_ratio[0][1] >= 0.5:
            logging.info('Musicbrainz replacing title "%s" with "%s" with score %s',
                         track['title'], by_ratio[0][0], by_ratio[0][1])
            track['title'] = by_ratio[0][0]
            mb_tracks.remove(by_ratio[0][0])


def guess_tracks(d):
    mb_tracks = get_tracks(d['artist'], d['album'])
    logging.info('Musicbrainz got track names for (%s, %s):\n%s\n', d['artist'], d['album'], pprint.pformat(mb_tracks))
    match_tracks(d, mb_tracks)
