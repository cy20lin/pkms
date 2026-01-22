from enum import Enum

class FileType(str, Enum):
    REGULAR   = "REGULAR"
    DIRECTORY = "DIRECTORY"
    # SYMLINK   = "SYMLINK"
    # PIPE      = "PIPE"

