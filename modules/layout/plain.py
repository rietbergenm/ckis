modname = "layout/plain"
moddesc = "Install seperate kernel files in /boot"
inputs = { "kernel" }
optinputs = {"initrd", "config", "symbols"}

def fire(self):
    outputs = {
        "kernel": f"vmlinuz-{self.kver}",
        "initrd": f"initrd.img-{self.kver}",
        "config": f"config-{self.kver}",
        "symbols": f"System.map-{self.kver}",
    }
    ret = []
    
    for f in {"kernel", "initrd", "config", "symbols"}:
        if f in self.inputs: # kernel is guaranteed to be there

            out = self.copy(self.inputs[f])
            out.path = self.boot / outputs[f]

            self.cp(self.inputs[f].path, out.path )

            out.installed = True

            ret += [ out ]


    return ret
