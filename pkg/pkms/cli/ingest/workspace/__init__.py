import argparse
import traceback

import commentjson as json
from loguru import logger

from pkms.core.utility import str_to_bool
from pkms.capability.ingest._capability import IngestCapability, IngestConfig, IngestRuntime, IngestState
from pkms.logging import NullLogger

def parse_args(argv:list[str]=None):
    parser = argparse.ArgumentParser(
        "pkms.cli.ingest",
        description="Ingest specified collection of owned file resources"
    )
    parser.add_argument("config_path")
    parser.add_argument('--dry-run', help='Just print instead of renaming the files',default=None, const=True, nargs='?', type=str_to_bool)
    parser.add_argument('--verbose', help='Print Verbosely',default=True, const=True, nargs='?', type=str_to_bool)
    return parser.parse_args(argv[1:])


def main(argv):
    args = parse_args(argv)
    logger.debug(f'load config, args.config_path={args.config_path}')
    config_json = {}
    with open(args.config_path, 'r') as f:
        config_json = json.load(f)
    config = IngestConfig(**config_json)
    runtime = IngestRuntime(config=config)
    capability = IngestCapability(runtime=runtime)
    capability.run(dry_run=args.dry_run)
    return 0

if __name__ == '__main__':
    import sys
    logger.remove()
    logger.add(sys.stderr, level="DEBUG")
    argv = sys.argv
    code = main(argv)
    sys.exit(code)