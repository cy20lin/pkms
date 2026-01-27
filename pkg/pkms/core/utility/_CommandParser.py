import argparse
from loguru import logger

class CommandParser:
    def __init__(self, name, description, sep='.'):
        self.sep = sep
        self.name = name
        self.parser = argparse.ArgumentParser(
            prog=name,
            description=description
        )
        self.subparsers = self.parser.add_subparsers(
            dest="command",
            required=True,
            metavar='command',
        )
        self.commands: dict = {}
    
    def add_command(self, name, command, descrpition=None):
        if descrpition is None:
            descrpition = f"Command {name}"
        self.subparsers.add_parser(
            name,
            help=descrpition
        )
        self.commands[name] = command

    def unknown_command(self, argv:list):
        """
        Signal error as a unknown command

        This command could be used with self.get_command(name,default=self.unknown_command)
        """
        assert len(argv)
        command = argv[0]
        args = argv[1:]
        self.parser.error(f"Unknown command={command} with args={args}")
    
    def get_command(self, subname, default=None):
        command = self.commands.get(subname, default)
        return command
    
    def parse(self, args):
        parsed_args, command_args = self.parser.parse_known_args(args)
        parsed_args.command_args = command_args
        parsed_args.command_argv = [parsed_args.command, *command_args]
        return parsed_args
    
    def error(self, message:str):
        return self.parser.error(message=message)