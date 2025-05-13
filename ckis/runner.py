import argparse
import sys
import tomllib

from .chain import Chain
from .config import load_config, sanitize_config
from .errors import ConfigError
from .persistence import store_run
from .pruning import prune_orphans


def handle_options():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--config",
        metavar = "file",
        type = argparse.FileType(mode = 'rb'),
        help = "configuration file to use"
    )


    subparsers = parser.add_subparsers(
        title = "command",
        dest = "cmd",
        required = True,
        help = "the command to run"
    )
    

    parser_run = subparsers.add_parser("run", help = "run one or more chains")

    parser_run.add_argument(
        "kver",
        type = str,
        help = "kernel version to run chain for"
    )
    parser_run.add_argument(
        "-c",
        "--chain",
        type = str,
        action = "append",
        help = "run only the specified chains"
    )
    parser_run.add_argument(
        "-u",
        "--until",
        type = str,
        default = "",
        help = "run until the specified link (globbing is supported)"
    )
    
    return parser.parse_args()


def get_chains(chains, conf):
    args_chain_names = set(chains) # don't handle the same chain twice
    conf_chain_names = map(lambda c: c["name"], conf["chains"])

    ret = []

    for name in args_chain_names:
        if name in conf_chain_names:
            ret += list(filter(lambda c: c["name"] == name, conf["chains"]))
        else:
            raise ConfigError(f"Chain '{name}' not found in config!")


    return ret



def do_run(args, conf):
    if args.chain:
        chains = get_chains(args.chain, conf)
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
