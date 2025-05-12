modname = "initrd/initramfs-tools"

def fire(self):
    initrd = self.Initrd(self.cwd / "initrd.img")   

    cmd = [ "mkinitramfs" ]
    cmd += [ "-o", initrd.path ]

    self.do(cmd)

    # return value can be list of artifacts or just one artifact.
    return initrd
