import pathlib

from collections import UserList


from .util import filter_class


class ArtifactPath:
    def __get__(self, obj, objtype=None):
        return obj._path

    def __set__(self, obj, value):
        obj._path = pathlib.Path(value).resolve()


class Artifact:
    def __init__(self, origin, *, installed=False, autoprune=True):
        self.origin = origin
        self.autoprune = autoprune
        self.installed = installed

class File(Artifact):
    path = ArtifactPath()

    def __init__(self, origin, path, **kwargs):
        super().__init__(origin, **kwargs)
        self.path = path


class Config(File):
    pass

class Symbols(File):
    pass

class Initrd(File):
    pass

# meta class used by signing tools
class Signable(File):
    def __init__(self, origin, path, *, signed=False, **kwargs):
        super().__init__(origin, path, **kwargs)
        self.signed = signed


class Kernel(Signable):
    pass

class Uki(Signable):
    pass



class ArtifactStore(UserList):
    def __init__(self, iterable=None):
        if iterable:
            iterable = map(self._check, iterable)

        super().__init__(iterable)

    def _reject(self):
        raise TypeError("Only Artifacts can be stored in ArtifactStore!")

    def _check(self, item):
        if isinstance(item, Artifact):
            return item
        else:
            self._reject()


    def __setitem__(self, key, item):
        self._check(item)
        self.data[key] = value


    def __getitem__(self, key):

        # convert string keys to their class equivalent
        if isinstance(key, str):
            classname = key.capitalize()
            if classname in globals():
                return filter_class(self.data, globals()[classname])
            else:
                raise KeyError("Key must be a valid Artifact subclass or int!")

        elif isinstance(key, type) and issubclass(key, Artifact):
            return filter_class(self.data, key)

        else:
            return self.data[key]


    def append(self, item):
        self._check(item)
        self.data.append(item)


    def insert(self, index, item):
        self._check(item)
        self.data.insert(index, item)


    def extend(self, other):
        list(map(self._check, other))

        self.data.extend(other)


    def __iadd__(self, other):
        # check for invalid types by exhausting the map
        list(map(self._check, other))

        self.data += other
