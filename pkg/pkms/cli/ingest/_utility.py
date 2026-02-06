import argparse
import pathlib
import commentjson as json
import os
from loguru import logger
from pkms.core.config import ConfigResolver

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

def resolve_workspace_config(args:argparse.Namespace, user_home_dir=None):
    if user_home_dir is None:
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
    return resolved_workspace_config