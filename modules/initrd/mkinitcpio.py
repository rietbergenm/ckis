modname = "initrd/mkinitcpio"

optconfig = { "MkinitcpioConfig" }
modoptions = { "MkinitcpioConfig": "file", "MkinitcpioHookDir": "dir" }

def fire(self):
    initrd = self.Initrd("initrd.img")

    cmd = [ "mkinitcpio" ]
    cmd += [ "--kernel", self.kver ]
    cmd += [ "-g", initrd.path ]

    if cfg := self.config.get("MkinitcpioConfig", None):
        cmd += [ "-c", cfg ]

    if hookdir := self.config.get("MkinitcpioHookDir", None):
        cmd += [ "-D", hookdir ]
        
    self.do(cmd)

    return initrd


