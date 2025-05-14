import sys
import tomllib

from .chain import Chain
from .cli import handle_options
from .config import load_config, sanitize_config
from .errors import ConfigError, DBKeyError
from .persistence import (
    delete_run,
    get_db,
    store_run,
)
from .pruning import prune_orphans, prune_run


def get_chainconfs(chains, conf):
    args_chain_names = set(chains) # don't handle the same chain twice
    conf_chain_names = set(map(lambda c: c["name"], conf["chains"]))

    ret = []

    for name in args_chain_names:
        if name in conf_chain_names:
            ret += list(filter(lambda c: c["name"] == name, conf["chains"]))
        else:
            raise ConfigError(f"Chain '{name}' not found in config!")


    return ret


def check_chains_in_db(chains):
    """
    Checks for each name in `chains` if it is has an entry in the db.
    If it does not, raise an error.

    Returns a set of all chain names that are in the database (so redunant
    names are discarded).
    """
    db = get_db()
    args_chain_names = set(chains)

    for name in args_chain_names:
        if not name in db:
            raise DBKeyError(f"Chain '{name}' not found in db!")

    return args_chain_names



def do_run(args, conf):
    if args.chain:
        chains = get_chainconfs(args.chain, conf)
    else:
        chains = conf["chains"]



    for chaincfg in chains:
        print(chaincfg)
        c = Chain(args.kver, chaincfg)
        c.run(until = args.until)

        # prune artifacts leftover by the previous run of this chain
        # for the same kernel version
        prune_orphans(c)

        # store this run so we can use this later to prune installed artifacts
        store_run(c)



def do_prune(args, conf):
    db = get_db()

    if args.chain:
        chain_names = check_chains_in_db(args.chain)
    else:
        # if no chains are specified, prune runs for all chains
        chain_names = set(db.keys())

    if args.kver:
        # prune all runs of this kernel version, regardless of config
        for chain in chain_names:
            if chain in db and args.kver in db[chain]:
                prune_run(chain, args.kver)
                delete_run(chain, args.kver)

        return

    print(chain_names)
    print(conf)

    for chainconf in get_chainconfs(chain_names, conf):
        # check in config how many kvers to keep (default to 2)

        name = chainconf.get("name")
        keep = chainconf.get("keep", 2)

        if keep == 0:
            # keep all kernel versions
            continue

        # sort kernel versions from highest to lowest
        # (alphabetical sort should suffice)
        kvers = list(db[name].keys())
        kvers.sort(reverse = True)

        # prune all but the last n
        for kver in kvers[keep:]:
            print((
                f"Pruning run for chain '{name}', "
                f"kernel version {kver}..."
            ))
            prune_run(name, kver)
            delete_run(name, kver)





def fire():
    # don't write bytecode when importing modules (as we don't want
    # __pycache__ directories cluttering /usr/lib/ckis)
    sys.dont_write_bytecode = True


    args = handle_options()

    if args.config:
        tomlconf = tomllib.load(args.config)
    else:
        tomlconf = load_config()

    conf = sanitize_config(tomlconf)

    match args.cmd:
        case "run":
            do_run(args, conf)

        case "prune":
            do_prune(args, conf)

        case _:
            raise NotImplementedError()
