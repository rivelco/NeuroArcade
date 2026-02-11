from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("neuroarcade")
except PackageNotFoundError:
    __version__ = "unknown"
