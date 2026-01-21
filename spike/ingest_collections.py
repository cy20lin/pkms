import sys
import argparse
import traceback

import commentjson as json
from loguru import logger as logging

from pkms.core.utility import str_to_bool
from pkms.app.ingest.app import App, AppConfig

def parse_args(argv:list[str]=None):
    parser = argparse.ArgumentParser("Ingest specified collection of owned file resources")
    parser.add_argument("config_path")
    parser.add_argument('--dry-run', help='Just print instead of renaming the files',default=None, const=True, nargs='?', type=str_to_bool)
    parser.add_argument('--verbose', help='Print Verbosely',default=True, const=True, nargs='?', type=str_to_bool)
    return parser.parse_args(argv[1:])

def main(argv):
    try:
        args = parse_args(argv)
        logging.debug(f'load config, args.config_path={args.config_path}')
        config_json = {}
        with open(args.config_path, 'r') as f:
            config_json = json.load(f)
        config = AppConfig(**config_json)
        app = App(config=config)
        app.run(dry_run=args.dry_run)
    except Exception as e:
        for s in traceback.format_exception(e):
            logging.critical(s)
        return 1
    return 0

if __name__ == '__main__':
    logging.remove()
    logging.add(sys.stderr, level="DEBUG")
    argv = sys.argv
    code = main(argv)
    sys.exit(code)
