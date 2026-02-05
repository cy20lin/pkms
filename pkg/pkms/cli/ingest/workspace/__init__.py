import argparse
import traceback
import os

import commentjson as json
from loguru import logger

from pkms.core.utility import str_to_bool
from pkms.capability.ingest._capability import IngestCapability, IngestConfig, IngestRuntime, IngestState
from pkms.logging import NullLogger
import pathlib

def parse_args(argv:list[str]=None):
    parser = argparse.ArgumentParser(
        "pkms.cli.ingest.workspace",
        description="Ingest specified collection of owned file resources"
    )
    parser.add_argument("--workspace-dir", help='Path to workspace dir', default=None)
    parser.add_argument("--config-path", help='Path to workspace config', default=None)
    parser.add_argument('--dry-run', help='Just print instead of renaming the files',default=None, const=True, nargs='?', type=str_to_bool)
    parser.add_argument('--verbose', help='Print Verbosely',default=True, const=True, nargs='?', type=str_to_bool)
    return parser.parse_args(argv[1:])

def get_worksapce_dir(args_workspace_dir, user_home_dir:pathlib.Path, getenv=os.getenv):
    env_workspace_dir = getenv("PKMS_WORKSPACE_DIR")
    default_workspace_dir = user_home_dir / ".pkms"
    logger.debug(f'env.PKMS_WORKSPACE_DIR={env_workspace_dir!r}')
    if args_workspace_dir:
        workspace_dir = pathlib.Path(args_workspace_dir).absolute()
    elif env_workspace_dir:
        workspace_dir = pathlib.Path(env_workspace_dir)
    else:
        workspace_dir = default_workspace_dir
    return workspace_dir

def get_workspace_config_path(args_config_path:str, workspace_dir: pathlib.Path):
    config_path = None
    if not args_config_path and workspace_dir:
        config_path = workspace_dir / 'config.jsonc'
    elif args_config_path:
        config_path = pathlib.Path(args_config_path)
    assert config_path
    return config_path

def load_json(file_path):
    config_json = {}
    with open(file_path, 'r') as f:
        config_json = json.load(f)
    return config_json

def resolve_workspace_config():
    pass

from pkms.core.config import ConfigResolver

def main(argv):
    args = parse_args(argv)
    user_home_dir = pathlib.Path.home()
    workspace_dir = get_worksapce_dir(args.workspace_dir, user_home_dir, os.getenv)
    workspace_config_path = get_workspace_config_path(args.config_path, workspace_dir)
    workspace_config_json = load_json(file_path=workspace_config_path)
    workspace_index_db_path = workspace_dir / 'index.db'
    logger.info(f'workspace_dir={workspace_dir}')
    logger.debug(f'workspace_config_path={workspace_config_path}')
    context = {
        'var': {
            "CURRENT_CONFIG_DIR": workspace_config_path.parent.as_posix(),
            "CURRENT_CONFIG_PATH": workspace_config_path.as_posix(),
            "USER_HOME_DIR": user_home_dir.as_posix(),
            "WORKSPACE_DIR": workspace_dir.as_posix(),
            "WORKSPACE_CONFIG_PATH": workspace_config_path.as_posix(),
            "WORKSPACE_INDEX_DB_PATH": workspace_index_db_path.as_posix(),
        },
        'env': os.environ,
        'args': vars(args),
    }
    resolver = ConfigResolver()
    resolved_workspace_config = resolver.resolve(root=workspace_config_json, context=context)
    config = IngestConfig(**resolved_workspace_config)

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