modname = "kernel/chimera"

def fire(self):
    cpath = f"/usr/lib/modules/{self.kver}/boot/config-{self.kver}"
    kpath = f"/usr/lib/modules/{self.kver}/boot/vmlinuz-{self.kver}"

    self.cp(cpath, "config")
    self.cp(kpath, "kernel")

    return [ self.Config("config"), self.Kernel("kernel") ]
