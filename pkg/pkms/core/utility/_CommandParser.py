import argparse
from loguru import logger

USE_DEFAULT_FALLBACK_COMMAND = object()
class CommandParser:
    USE_DEFAULT_FALLBACK_COMMAND = USE_DEFAULT_FALLBACK_COMMAND
    def __init__(self, name, description, sep='.'):
        self.sep = sep
        self.name = name
        self.parser = argparse.ArgumentParser(
            prog=name,
            description=description,
            usage=f"{name} [options...] <command> ...",
            add_help=False
        )
        self.commands: dict = {}
        self.descriptions: dict = {}
    
    def print_help(self):
        self.parser.print_help()
        print('')
        print("command:")
        for name,description in self.descriptions.items():
            print(f"  {name}: {description}")

    def add_command(self, name, command, descrpition=None):
        if descrpition is None:
            descrpition = f"Command {name}"
        self.commands[name] = command
        self.descriptions[name] = descrpition

    def default_fallback_command(self, argv:list):
        """
        Signal error as a unknown command

        This command could be used with self.get_command(name,default=self.unknown_command)
        """
        command = argv[0] if argv else None
        args = argv[1:]
        logger.debug(f"Unknown command={command!r} with args={args!r}")
        self.print_help()
        return 1
    
    def get_command(self, subname, default=USE_DEFAULT_FALLBACK_COMMAND):
        if default is USE_DEFAULT_FALLBACK_COMMAND:
            default = self.default_fallback_command
        command = self.commands.get(subname, default)
        return command
    
    def parse(self, args):
        parsed_args, command_argv = self.parser.parse_known_args(args)
        parsed_args.command = command_argv[0] if command_argv else None
        parsed_args.command_args = command_argv[1:]
        parsed_args.command_argv = command_argv
        return parsed_args
    
    def error(self, message:str):
        return self.parser.error(message=message)