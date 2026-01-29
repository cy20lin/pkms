from pkms.capability.dispatcher import WindowsDispatcherInstaller
import os
import pathlib
from dataclasses import asdict
import json
from loguru import logger as logging


def do_install(argv: list[str]) -> int:
    logging.error(f'command dispatcher install not supported on this os={os.name!r}')
    return 1

def do_status(argv: list[str]) -> int:
    logging.error(f'command dispatcher status not supported on this os={os.name!r}')
    return 1

def do_uninstall(argv: list[str]) -> int:
    logging.error(f'command dispatcher uninstall is not supported on this os={os.name!r}')
    return 1

def main(argv: list[str] | None = None) -> int:
    from pkms.core.utility import CommandParser
    args = argv[1:] if argv is not None else []
    parser = CommandParser(
        name="pkms.cli.dispatcher",
        description="PKMS command line interface"
    )
    DispatcherInstaller = None
    config = {}
    if os.name == 'nt':
        DispatcherInstaller = WindowsDispatcherInstaller
        project_root_path= pathlib.Path(__file__).parents[4]
        executable_path = project_root_path / 'bin' / 'pkms.cmd'
        config = {
            'executable_path': executable_path
        }

    if DispatcherInstaller is not None:
        dispatcher_installer = DispatcherInstaller(**config)
        def do_install(argv: list[str]) -> int:
            dispatcher_installer.install()
            return 0
        def do_status(argv: list[str]) -> int:
            status = dispatcher_installer.status()
            status_json_str = json.dumps(asdict(status), indent=4)
            print(f'{status_json_str}')
            return 0
        def do_uninstall(argv: list[str]) -> int:
            result = dispatcher_installer.uninstall()
            return 0 if result is True else 1
        
    parser.add_command("install", do_install , "")
    parser.add_command("status", do_status, "")
    parser.add_command("uninstall", do_uninstall, "")
    parsed_args = parser.parse(args)
    command = parser.get_command(parsed_args.command)
    code = command(parsed_args.command_argv)
    return code

__all__ = ['main']

if __name__ == '__main__':
    import sys
    argv = sys.argv
    code = main(argv)
    sys.exit(code)
