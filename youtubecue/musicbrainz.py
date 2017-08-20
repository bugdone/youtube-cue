import difflib

import musicbrainzngs


musicbrainzngs.set_useragent('youtube-cue', '0.1')


def get_tracks(artist, album):
    recordings = musicbrainzngs.search_recordings(artist=artist, release=album)['recording-list']
    return [r['title'] for r in recordings]


def match_tracks(cue, mb_tracks):
    mb_tracks = set(mb_tracks)
    for track in cue['tracks']:
        if len(mb_tracks) == 0:
            return
        by_ratio = sorted([(t, difflib.SequenceMatcher(a=track['title'], b=t).ratio()) for t in mb_tracks],
                          key=lambda x: -x[1])
        if by_ratio[0][1] >= 0.5:
            track['title'] = by_ratio[0][0]
            mb_tracks.remove(by_ratio[0][0])


def guess_tracks(d):
    mb_tracks = get_tracks(d['artist'], d['album'])
    match_tracks(d, mb_tracks)
