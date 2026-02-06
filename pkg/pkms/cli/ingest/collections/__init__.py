import argparse
import traceback
import os

import commentjson as json
from loguru import logger

from pkms.core.utility import str_to_bool
from pkms.capability.ingest._capability import IngestCapability, IngestConfig, IngestRuntime, IngestState
from pkms.logging import NullLogger
import pathlib
from pkms.core.model import FileLocation

def parse_args(argv:list[str]=None):
    parser = argparse.ArgumentParser(
        "pkms.cli.ingest.collections",
        description="Ingest specified collections"
    )
    parser.add_argument("collctions", help='Path to collection dirs', nargs='*')
    parser.add_argument("--workspace-dir", help='Path to workspace dir', default=None)
    parser.add_argument("--config-path", help='Path to workspace config', default=None)
    parser.add_argument('--dry-run', help='Just print instead of renaming the files',default=None, const=True, nargs='?', type=str_to_bool)
    parser.add_argument('--verbose', help='Print Verbosely',default=True, const=True, nargs='?', type=str_to_bool)
    return parser.parse_args(argv[1:])

from .._utility import resolve_workspace_config
import os

def main(argv):
    args = parse_args(argv)
    workspace_config = resolve_workspace_config(args)

    config = IngestConfig(**workspace_config)
    runtime = IngestRuntime(config=config)
    capability = IngestCapability(runtime=runtime)
    path_convention = 'windows' if os.name == 'nt' else 'posix'
    collection_paths = [pathlib.Path(collection_path).absolute().as_posix()
        for collection_path in args.collections
    ]
    collection_locations = [FileLocation.from_filesystem_path(
        collection_path, path_convention=path_convention
    ) for collection_path in collection_paths]
    capability.ingest_collections(collection_locations, dry_run=args.dry_run)

    return 0

if __name__ == '__main__':
    import sys
    logger.remove()
    logger.add(sys.stderr, level="DEBUG")
    argv = sys.argv
    code = main(argv)
    sys.exit(code)