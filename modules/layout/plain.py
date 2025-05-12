modname = "layout/plain"
moddesc = "Install seperate kernel files in /boot"
inputs = { "kernel" }
optinputs = {"initrd", "config", "symbols"}

def fire(self):
    outputs = {
        "kernel": self.esp / f"vmlinuz-{self.kver}",
        "initrd": self.esp / f"initrd.img-{self.kver}",
        "config": self.esp / f"config-{self.kver}",
        "symbols": self.esp / f"System.map-{self.kver}",
    }
    ret = []
    
    for f in {"kernel", "initrd", "config", "symbols"}:
        if f in self.inputs: # kernel is guaranteed to be there

            self.cp(self.inputs[f].path, outputs[f])

            out = self.copy(self.inputs[f])
            out.path = outputs[f]
            out.installed = True

            ret += [ out ]


    return ret
