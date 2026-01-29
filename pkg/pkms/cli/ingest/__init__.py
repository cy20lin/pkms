from . import file
from . import files
from . import collection
from . import collections
from . import workspace

def main(argv: list[str] | None = None) -> int:
    from pkms.core.utility import CommandParser
    args = argv[1:] if argv is not None else []
    parser = CommandParser(
        name="pkms.cli.ingest",
        description="PKMS Ingestion utility"
    )
    parser.add_command("file", file.main, "Ingest a file")
    parser.add_command("files", file.main, "Ingest files")
    parser.add_command("collection", file.main, "Ingest a collection")
    parser.add_command("collections", file.main, "Ingest collections")
    parser.add_command("workspace", workspace.main, "Ingest a workspace")
    parsed_args = parser.parse(args)
    command = parser.get_command(parsed_args.command)
    code = command(parsed_args.command_argv)
    return code

if __name__ == '__main__':
    import sys
    argv = sys.argv
    code = main(argv)
    sys.exit(code)
