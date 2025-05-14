import sys
import tomllib

from .chain import Chain
from .cli import handle_options
from .config import load_config, sanitize_config
from .errors import ConfigError
from .persistence import store_run
from .pruning import prune_orphans


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

        case _:
            raise NotImplementedError()
