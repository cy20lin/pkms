__version__='0.0.1'
from . import cli
from . import web

def main(argv: list[str] | None = None) -> int:
    from pkms.core.utility import CommandParser
    args = argv[1:] if argv is not None else []
    parser = CommandParser(
        name="pkms",
        description="Personal Knowledge Management System"
    )
    parser.add_command("cli", cli.main, "Command Line Interface")
    parser.add_command("web", web.main, "Web User Interface")
    parsed_args = parser.parse(args)
    command = parser.get_command(parsed_args.command)
    code = command(parsed_args.command_argv)
    return code

if __name__ == '__main__':
    import sys
    argv = sys.argv
    code = main(argv)
    sys.exit(code)