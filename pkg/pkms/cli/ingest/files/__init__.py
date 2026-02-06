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
        "pkms.cli.ingest.files",
        description="Ingest specified collection of owned file resources"
    )
    parser.add_argument("files", help='Paths to files to ingest', nargs='*')
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
    file_paths = [pathlib.Path(file_path).absolute().as_posix()
        for file_path in args.files
    ]
    file_locations = [FileLocation.from_filesystem_path(
        file_path, path_convention=path_convention
    ) for file_path in file_paths]
    capability.ingest_files(file_locations, dry_run=args.dry_run)

    return 0

if __name__ == '__main__':
    import sys
    logger.remove()
    logger.add(sys.stderr, level="DEBUG")
    argv = sys.argv
    code = main(argv)
    sys.exit(code)