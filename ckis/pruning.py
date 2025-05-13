from .errors import DBKeyError
from .persistence import get_stored_run
from .util import filter_value

def get_orphaned_paths(c):
    try:
        prev_run = get_stored_run(c.name, c.kver)

    except DBKeyError:
        # there is no previous run in the db,
        # so there are no orphaned paths

        return set()


    installed = filter_value(c.store, "installed", True)

    curr_paths = { art.path for art in installed }
    prev_paths = { art.path for art in prev_run["store"] }

    return prev_paths - curr_paths



# prunes all artifacts installed by an earlier run
# of this chain for the same kernel version
# that were not replaced after the chain finished running
# this happens for example when the config changes and
# one changes from a bare to uki layout
def prune_orphans(c):
    for path in get_orphaned_paths(c):
        # don't care if the file is missing,
        # we just want it to be gone
        path.unlink(missing_ok = True)
