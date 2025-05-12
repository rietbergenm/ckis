modname = "initrd/uefisign"
moddesc = "sign an EFI executable with uefisign"

inputs = { "signable" } # something we can sign (kernel or uki)
config = { "sbkey", "sbcert" }


def fire(self):
    # don't know if this is a kernel or uki or efi binary (bootloader)
    # all we know it is from the Signable class, so it has the .signed
    # attribute.
    image = self.copy(self.inputs["signable"])
    image.path = "signed.efi"

    cmd = [ "uefisign" ]
    cmd += [ "-c", self.config["sbcert"] ]
    cmd += [ "-k", self.config["sbkey"] ]
    cmd += [ "-o", image.path ]
    cmd += [ self.inputs["signable"].path ]
    
    self.do(cmd)

    image.signed = True

    return image
