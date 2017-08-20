import json
import sys

import youtubecue


if __name__ == '__main__':
    print json.dumps(youtubecue.get_cue(sys.argv[1]), indent=4)
