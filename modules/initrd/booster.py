modname = "initrd/booster"

modoptions = { "BoosterConfFile": "file" }
optconfig = { "BoosterConfFile" }

def fire(self):
    initrd = self.Initrd("initrd.img")

    cmd = [ "booster", "build" ]
    cmd += [ "--kernel-version", self.kver ]

    if conffile := self.config.get("BoosterConfFile", None):
        cmd += [ "--config", conffile ]

    cmd += [ initrd.path ]

    self.do(cmd)

    return initrd

