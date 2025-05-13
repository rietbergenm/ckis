class ConfigError(Exception):
    pass

class DBError(Exception):
    pass

class DBKeyError(DBError, KeyError):
    pass

class ModuleError(Exception):
    pass
