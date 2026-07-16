from importlib.metadata import PackageNotFoundError, version


def version_string() -> str:
    try:
        return version("updee")
    except PackageNotFoundError:
        return "unknown"
