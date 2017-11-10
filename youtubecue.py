import json
import sys
import os

import youtubecue


if __name__ == '__main__':
    if 'youtubecue_log_dir' in os.environ:
        youtubecue.set_log_directory(os.environ.get('youtubecue_log_dir'))
    print json.dumps(youtubecue.get_cue(sys.argv[1]), indent=4)
