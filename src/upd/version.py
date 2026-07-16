from importlib.metadata import PackageNotFoundError, version


def version_string() -> str:
    try:
        return version("upd")
    except PackageNotFoundError:
        return "unknown"
