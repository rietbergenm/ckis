import csv
import os
import pathlib

def to_path(cwd, path):
    '''Convert a string or Path object to a path. If it is a relative path,
    make it relative to the current working directory.
    '''

    # make sure we have a path; the TypeError thrown by this is clear enough
    path = pathlib.Path(path)

    if path.is_absolute():
        return path
    else:
        return cwd / path


def to_list(val):
    if not isinstance(val, list):
        val = [ val ]

    return val


def get_classname(instance):
    c = getattr(instance, "__class__")
    return getattr(c, "__name__")


def filter_class(iterable, baseclass):
    f = lambda x: isinstance(x, baseclass)
    l = filter(f, iterable)

    # return list to retain order of the iterable
    return list(l)


def search_esp_paths():
    # common locations for esp in order of likeliness.
    # it is still recommended to set it manually in config.toml
    for path in [ "/efi", "/boot/efi", "/boot" ]:
        p = pathlib.Path(path)
        if p.is_dir():
            return p

    # if none of these match, give up
    return None
