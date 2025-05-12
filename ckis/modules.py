import pathlib
import importlib.util

from .errors import ConfigError

module_cache = {}

def find_module(name):
    moddirs = [
        "/etc/ckis/modules",
        "/usr/local/lib/ckis/modules",
        "/usr/lib/ckis/modules",
    ]

    for moddir in moddirs:
        path = pathlib.Path(moddir) / (name + ".py")
        if path.is_file():
            return path

    # no module found
    return None


# path needs to be a pathlib.Path
def import_path(path):
    modname = path.name.removesuffix(".py")
    modspec = importlib.util.spec_from_file_location(modname, path)
    mod = importlib.util.module_from_spec(modspec)
    modspec.loader.exec_module(mod)

    return mod
    


def get_module(link):
    global module_cache

    if link in module_cache:
        return module_cache[link]
    else:
        modpath = find_module(link)

        if not modpath:
            raise ConfigError(
                f"Module {link} not found in search path!"
            )
        
        mod = import_path(modpath)
        validate_module(mod)
        module_cache[link] = mod  # cache the module
        return mod


mod_fields = [
    "modname",
    "moddesc",
    "modoptions",
    "config",
    "optconfig",
    "inputs",
    "optinputs",
]

def validate_module(mod):
    # we need
    # ! modname
    # ! moddesc
    # ? modoptions
    # ? config
    # ? optconfig
    # ? inputs
    # ? optinputs
    # ? fire (the function)


    if hasattr(mod, "modname"):
        validate_modname(mod)
    else:
        raise ValueError(f"{mod.__file__}: 'modname' is required!")

    if hasattr(mod, "moddesc"):
        validate_moddesc(mod)
    # XXX: will be required in the future
    #else:
    #    raise ValueError(f"{mod.modname}: 'moddesc' is required!")


    if hasattr(mod, "modoptions"):
        validate_modoptions(mod)

    for field in ("config", "optconfig", "inputs", "optinputs"):
        if hasattr(mod, field):
            validate_set_of_strings(mod, field)
    
    if (hasattr(mod, "config")
        and hasattr(mod, "optconfig")
        and len(mod.config & mod.optconfig) > 0
    ):
        raise ValueError(
            (f"{mod.modname}: settings can only be specified in either"
             " 'config' or 'optconfig', not both!")
        )

    if (hasattr(mod, "inputs")
        and hasattr(mod, "optinputs")
        and len(mod.inputs & mod.optinputs) > 0
    ):
        raise ValueError(
            (f"{mod.modname}: inputs can only be specified in either"
             " 'inputs' or 'optinputs', not both!")
        )


    # unused variables are treated as errors
    validate_vars(mod)





def validate_set_of_strings(mod, name):
    attr = getattr(mod, name)

    if type(attr) != set:
        raise TypeError(f"{mod.modname}: '{name}' should be a set!")
    elif not all(type(key) is str for key in attr):
        raise TypeError(
            f"{mod.modname}: '{name}' should only contain strings!"
        )

def validate_modoptions(mod):
    modopts = mod.modoptions

    if type(modopts) != dict:
        raise TypeError(f"{mod.modname}: 'modoptions' should be a dict!")
    elif not all(type(key) is str for key in modopts.keys()):
        raise TypeError(
            f"{mod.modname}: modoptions' setting names should be strings!"
        )
    elif not all(type(val) is str for val in modopts.values()):
        raise TypeError(
            f"{mod.modname}: modoptions' setting types should be strings!"
        )


def validate_modname(mod):
    modname = mod.modname

    if type(modname) != str:
        raise TypeError(f"{mod.modname}: 'name' should be a string!")
    
    # enforce category/name format?

    pass


def validate_moddesc(mod):
    moddesc = mod.moddesc

    if type(moddesc) != str:
        raise TypeError(f"{mod.modname}: 'moddesc' should be a string!")



def validate_vars(mod):
    global mod_fields
    
    for fld, val in vars(mod).items():
        if fld.startswith("_"):
            # private fields starting with "_" are allowed
            continue
        else:
            if callable(val):
                # custom toplevel functions are allowed 
                continue
            elif fld in mod_fields:
                # it is one of the known fields
                continue
            else:
                raise ValueError(f"{mod.modname}: unknown field: {fld}")




