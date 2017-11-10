import argparse
import json
import os

import youtubecue

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('url', help='youtube url')
    parser.add_argument('--musicbrainz-app', dest='musicbrainz_app')
    parser.add_argument('--musicbrainz-version', dest='musicbrainz_version')
    args = parser.parse_args()

    if args.musicbrainz_app and args.musicbrainz_version:
        youtubecue.init_musicbrainz(args.musicbrainz_app, args.musicbrainz_version)
    if 'youtubecue_log_dir' in os.environ:
        youtubecue.set_log_directory(os.environ.get('youtubecue_log_dir'))
    print json.dumps(youtubecue.get_cue(args.url), indent=4)
