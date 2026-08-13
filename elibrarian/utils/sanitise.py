import re


def sanitise_name(value: str) -> str:
    """
    Make a metadata value suitable for use as a filesystem name.
    """

    value = value.strip()

    # Replace characters that are awkward/unsafe in filenames.
    value = re.sub(r'[<>:"/\\|?*]', "-", value)

    # Collapse repeated whitespace.
    value = re.sub(r"\s+", " ", value)

    # Avoid trailing spaces/dots.
    value = value.rstrip(". ")

    return value
