import copy
import fnmatch
import os
import pathlib
import platform
import shutil
import subprocess
import tempfile

from . import artifacts
from .errors import ConfigError, ModuleError
from .modules import get_module
from .util import filter_class, to_list, to_path, search_esp_paths



class Chain:
    def __init__(self, kver, config):
        self.kver = kver
        self._config = config

        self.cwd = pathlib.Path(os.getcwd())
        self._dirstack = []
        
        # convenience properties
        self.name = config["name"]

        self.boot = config.get("boot", pathlib.Path("/boot"))

        if esp := config.get("esp", None):
            self.esp = esp
        elif esp := search_esp_path():
            self.esp = esp
        else:
            # esp not specified and couldn't detect it
            # highly unlikely as this requires /boot not to be present
            raise ConfigError("Failed to determine location of the esp!")


        # only works if /etc/os-release or /usr/lib/os-release is present
        self.osrelease = platform.freedesktop_os_release()
        

        # state variables
        self.config = {}
        self.inputs = {}

        self.store = artifacts.ArtifactStore()


        # import modules
        self.links = {}
        for link in self._config["links"]:
            mod = get_module(link)
            
            self.links[link] = mod



    def run(self, until=""):
        '''
        Run all phases of the chain. Until is a glob pattern to be matched
        against the links. After the current link matches the pattern.
        Execution is terminated.
        '''

        self.prepare()

        if until == "prepare":
            return

        for link in self.links:
            self._run_link(link)
            if fnmatch.fnmatch(link, until):
                return

        self.cleanup()



    def _fire_link(self, hook, *args, **kwargs):
        func = getattr(self.links[hook], "fire")

        # Links are imported from modules; they are not methods,
        # so we need to supply the 'self' argument manually.
        # also they don't take other arguments
        return func(self)


    def _run_link(self, link):

        self.pushd(link)
        self._prepare_inputs(link)
        self._prepare_config(link)

        ret = self._fire_link(link)

        # allow links to return a single item if
        # it only produces one artifact
        ret = to_list(ret)

        self.store.extend(ret)

        self.config = {}
        self.inputs = {}
        self.popd()

        
    def _prepare_inputs(self, link):
        reqs = getattr(self.links[link], "inputs", set())
        wants = getattr(self.links[link], "optinputs", set())

        self.inputs = {}

        for art in reqs | wants:

            # look for produced artifacts of the specified class
            l = self.store[art]

            if len(l) != 0:

                # for now, always take the most recent of this type
                self.inputs[art] = l[-1] 

            elif art in reqs:
                raise ModuleError(f"Required artifact {art} not ready!")

    

   
    def _prepare_config(self, link):
        reqs = getattr(self.links[link], "config", set())
        wants = getattr(self.links[link], "optconfig", set())

        self.config = {}

        # config should be sanitized, so required keys are all present
        for key in reqs | wants:
            if key in self._config:
                self.config[key] = self._config[key]
            


    

    ################## internal phases ##################



    # might be common to all chains but is indeed a phase
    def prepare(self):
        self.tmpdir = tempfile.TemporaryDirectory(
            prefix = f"chain-{self.name}-{self.kver}."
        )
        self.pushd(self.tmpdir.name)

        for link in self.links:
            (self.cwd / link).mkdir(parents = True)


    def cleanup(self):
        self.popd()
        self.tmpdir.cleanup()


    ######## artifact classes ##########

    Config = artifacts.Config

    Symbols = artifacts.Symbols

    Initrd = artifacts.Initrd

    Signable = artifacts.Signable

    Kernel = artifacts.Kernel

    Uki = artifacts.Uki

    ########### utility functions ############
    

    def pushd(self, directory):
        self._dirstack.append(self.cwd)
        self.cwd = to_path(self.cwd, directory)
        os.chdir(self.cwd)


    def popd(self):
        self.cwd = self._dirstack.pop()
        os.chdir(self.cwd)


    def cp(self, srcp, destp, recursive=False, symlinks=True):
        '''Copy srcp to destp. If either of these is relative, it will be
        seen as relative to the temporary working directory. To copy a
        directory tree, set recursive=True. Symlinks are copied as-is,
        unless symlinks=False, then they are dereferenced.

        Returns the path of the created path.
        '''
        destp = to_path(self.cwd, destp)
        srcp = to_path(self.cwd, srcp)

        if recursive and srcp.is_dir():
            if destp.is_dir():
                destp = destp / srcp.name
            else:
                ret = shutil.copytree(
                    srcp, destp, symlinks=symlinks, dir_exist_ok=True,
                )
        elif srcp.is_dir():
            # todo: better error propagation
            raise ModuleError("Not copying directory when recurive is False.")
        else:
            ret = shutil.copy2(srcp, destp, follow_symlinks=symlinks)

        return pathlib.Path(ret)


    def mkdir(self, path, parents=False):
        return to_path(self.cwd, path).mkdir(
            parents=parents, exist_ok=parents
        )

    # why bother? by wrapping the functions, modules don't have to import
    # libraries themselves. They use self.do instead of subprocess.run.

    def do(self, *args, **kwargs):
        return subprocess.run(*args, **kwargs)



    def copy(self, obj):
        return copy.copy(obj)


