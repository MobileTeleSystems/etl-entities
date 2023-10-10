from typing import Optional, Type


def deprecated(version: Optional[str] = None):  # noqa: WPS473
    def decorator(cls: Type) -> Type:
        version_note = f" since version {version}" if version else ""
        cls.__doc__ = (
            f".. deprecated:: {version}\n"
            f"   The `{cls.__name__}` class is deprecated{version_note}"
            " and will be removed in a future version.\n\n"
            f"{cls.__doc__}"
        )
        return cls

    return decorator
