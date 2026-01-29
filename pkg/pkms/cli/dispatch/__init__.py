from pkms.component.resolver import UriResolver
from pkms.core.model import ResolvedTarget

from loguru import logger

import os.path
import os
import argparse
import pathlib
import requests
import webbrowser
import os
import sys

def server_ready(base_url: str, timeout=0.05) -> bool:
    try:
        r = requests.get(f"{base_url}/api/ready", timeout=timeout)
        return r.status_code == 200
    except Exception:
        return False

class UriHandler:
    def handle(self, target: ResolvedTarget) -> None:
        # file:///C:/path/to/file.html -> C:/path/to/file.html
        path_convention = 'windows' if os.name == 'nt' else 'posix'
        path = target.file_location.to_filesystem_path(path_convention=path_convention)

        if not os.path.exists(path):
            raise FileNotFoundError(path)
        
        base_url = 'http://localhost:43472'
        if server_ready(base_url, timeout=0.05):
            url = f'{base_url}/api/view/{target.file_id}{target.file_extension}'
            webbrowser.open(url)
        else:
            os.startfile(path)


def parse_args(argv:list[str]=None):
    parser = argparse.ArgumentParser(
        "pkms.cli.dispatch",
        description="Resolve PKMS URI dispatch file to system app"
    )
    parser.add_argument("uri", help='The pkms uri to dispatch')
    return parser.parse_args(argv[1:])

def main(argv: list[str]) -> int:
    args = parse_args(argv)
    default_workspace_dir = pathlib.Path.home() / ".pkms"
    env_workspace_dir = os.getenv("PKMS_WORKSPACE_DIR")
    logger.debug(f'env.PKMS_WORKSPACE_DIR={env_workspace_dir!r}')
    if env_workspace_dir:
        workspace_dir = pathlib.Path(env_workspace_dir)
    else:
        workspace_dir = default_workspace_dir

    db_path = workspace_dir / 'index.db'
    db_path_str = db_path.as_posix()
    config = UriResolver.Config(
        db_path=db_path_str
    )
    resolver = UriResolver(config=config)
    handler = UriHandler()

    try:
        target = resolver.resolve(args.uri)
        handler.handle(target)
    except Exception as e:
        logger.critical(f"[PKMS URI ERROR] {e}", file=sys.stderr)
        return 2

if __name__ == '__main__':
    logger.remove()
    logger.add(sys.stderr, level="DEBUG")
    argv = sys.argv
    code = main(argv)
    sys.exit(code)