import shelve

from .artifacts import ArtifactStore
from .errors import DBError, DBKeyError
from .util import filter_value

DBPATH = "/var/lib/ckis/db"

def store_run(chain):
    obj = {}
    
    # We only need to prune installed artifacts;
    # emphemeral ones are cleared with the tmpdir.
    obj["store"] = ArtifactStore(filter_value(chain.store, "installed", True))
    
    with shelve.open(DBPATH) as s:
        if not chain.name in s:
            s[chain.name] = {}

        runs = s[chain.name]
        runs[chain.kver] = obj
        s[chain.name] = runs


def delete_run(name: str, kver: str):
    with shelve.open(DBPATH, 'w') as s:
        if name in s and kver in s[name]:
            runs = s[name]
            runs.pop(kver)
            s[name] = runs
        else:
            raise DBKeyError((
                f"Can't remove run of chain {name} for kernel version {kver}, "
                "as it is not in db."
            ))


def get_stored_run(name, kver):
    with shelve.open(DBPATH, 'r') as s:
        if name in s and kver in s[name]:
            return s[name][kver]
        else:
            raise DBKeyError((
                f"Run of chain {name} for kernel version "
                f"{kver} not found in db."
            ))



