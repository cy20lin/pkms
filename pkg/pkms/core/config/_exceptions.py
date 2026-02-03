"""Custom exceptions for the config resolver package."""

class ConfigResolutionError(RuntimeError):
    """Raised when the configuration resolution process exceeds limits or encounters
    an unrecoverable error.
    """
    pass
