from .errors import ConfigError
from .modules import get_module
import copy
import os
import pathlib
import tomllib


# XXX: what is the best way to handle default values?
# setting it if nothing is present makes inheriting harder
core_opts = [
    # name      type    mand    source
    ("esp",     "dir",  False,  "core"),
    ("sbcert",  "file", False,  "core"),
    ("sbkey",   "file", False,  "core"),
]



def has_key(obj, name, keytype):
    return (name in obj) and isinstance(obj[name], keytype)


def check_file(path):
    return pathlib.Path(path).is_file()

def check_dir(path):
    return pathlib.Path(path).is_dir()

def err_key_mand(key, src):
    raise ConfigError(f"Option '{key}' required by module '{src}' is not set!")


# when called, we have verified value has the correct base type,
# so for our type of "path", we can assume value is a string
def sanitize_key_value(config, opt):
    key, tp, mand, src = opt # item of config_options

    match tp:
        case "dir":
            if has_key(config, key, str):
                path = pathlib.Path(config[key])
                if path.is_dir():
                    return path
                else:
                    raise ConfigError(f"Cannot open directory '{path}'!")
            elif mand:
                err_key_mand(key, src)
            
        case "file":
            if has_key(config, key, str):
                path = pathlib.Path(config[key])
                if path.is_file():
                    return path
                else:
                    raise ConfigError(f"Cannot read file '{path}'!")
            elif mand:
                err_key_mand(key, src)
        
        case _:
            raise ConfigError(f"Unkown type: '{tp}'!")


def load_config(conf_file=None):

    filen = None

    # XXX: move this to other function (runner?)

    if conf_file:
        if os.access(conf_file, os.R_OK):
            filen = conf_file 
        else:
            raise PermissionError("Cannot read specified config file!")
    else:
        dlocs = [ "/etc/ckis/config.toml" ]

        for f in dlocs:
            if os.access(f, os.F_OK):
                # stop at the first file that is in the list and exists.
                # If it is not readable, we are propably not running as
                # the right user (root). It is unlikely that the file
                # perms are bad, so consider it an error.
                if os.access(f, os.R_OK):
                    filen = f
                else:
                    raise PermissionError(
                        f"Configuration file {f} found, \
                        but it is not readable."
                    )
    
    # do we want to error if there is no config?
    if not filen:
        raise ConfigError("No configuration file found!")

            
    with open(filen, 'rb') as cfg:
        config = tomllib.load(cfg)


    return config


# make sure settings are valid and parse them
def sanitize_config(config):
    vcfg = {} # valid config
    chain_names = []


    ###### load global config  #######
    #### shared across all chains ####

    if has_key(config, "global", dict):
        globcfg = config["global"]
    elif "global" in config:
        raise ConfigError("Key 'global' should be a table!")
    else:
        globcfg = {}



    ### chains ###

    if has_key(config, "chains", list):
        vcfg["chains"] = []

        for chain in config["chains"]:
            vchain, chain_opts = sanitize_chain(chain)
            
            if vchain["name"] in chain_names:
                raise ConfigError(f"Chain '{vchain["name"]}' defined twice!")

            # Parse global settings w.r.t. options allowed by this chain
            vglob = sanitize_settings(globcfg, chain_opts)

            vchain = vglob | vchain # chain overwrites global settings

            check_required_opts(vchain)
            
            vcfg["chains"] += [ vchain ]
            chain_names += [ vchain["name"] ]

    else:
        raise ConfigError("Configuration must specify at least one chain!")

    return vcfg



# here we assume 'chains' section exists.
def sanitize_chain(chain):
    vchain = {} # valid chain

    if has_key(chain, "name", str):
        vchain["name"] = chain["name"]
    else:
        raise ConfigError(f"Chain must have a name!")


    ### Parse links ###
    # This needs to happen first, so we know what modules we are loading
    # We need these to determine the available settings.

    vchain["links"] = []

    # only add core_opts to chain_opts, don't assign and change core_opts
    # by changing chain_opts (passing by reference)
    chain_opts = []
    chain_opts += core_opts

    if has_key(chain, "links", list):
        for link in chain["links"]:
            if isinstance(link, str):
                mod = get_module(link)

                chain_opts += get_mod_opts(mod)

                vchain["links"] += [ link ]

            else:
                raise ConfigError("Link names should be strings!")



    ### Parse settings ###

    vsettings = sanitize_settings(chain, chain_opts)
    vchain |= vsettings

    return vchain, chain_opts



def sanitize_settings(config, options):
    ret = {}

    for key, tp, mand, src in options:
        val = sanitize_key_value(config, (key, tp, mand, src))
        if val:
            ret[key] = val

    return ret


# module has been verified
def get_mod_opts(mod):
    mod_opts = []

    if hasattr(mod, "modoptions"):
        for name, tp in mod.modoptions.items():
            # custom mod options are never mandatory system-wide
            # they can still be part of mod.config and will be required for 
            # this module in that case,
            # but that is different from being globally mandatory.
            mod_opts += [(name, tp, False, mod.modname)]


    return mod_opts


# chain has been sanitized
# this checks if all config options that modules specify in `config`
# are present.
def check_required_opts(chain):
    for link in chain["links"]:
        mod = get_module(link)
        if hasattr(mod, "config"):
            for key in mod.config:
                if not key in chain:
                    raise ConfigError((
                        f"Key '{key}' required by link '{link}'"
                       f" of chain '{chain["name"]}' not set!"
                    ))

