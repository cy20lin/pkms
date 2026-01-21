from . import ingest

def main(argv: list[str] | None = None) -> int:
    from pkms.core.utility import CommandParser
    args = argv[1:] if argv is not None else []
    parser = CommandParser(
        name="pkms.cli",
        description="PKMS command line interface"
    )
    parser.add_command("ingest", ingest.main, "Ingest collections")
    parsed_args = parser.parse(args)
    command = parser.get_command(parsed_args.command)
    code = command(args)
    return code

if __name__ == '__main__':
    import sys
    argv = sys.argv
    code = main(argv)
    sys.exit(code)
