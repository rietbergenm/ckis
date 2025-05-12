modname = "signing/sbsigntools"

config = { "sbkey", "sbcert" }
inputs = { "signable" }

def fire(self):
    infile = self.inputs["signable"]
    out = self.copy(infile)
    out.path = str(infile.path.name) + ".signed"

    cmd = [ "sbsign" ]
    cmd += [ "--key", self.config["sbkey"] ]
    cmd += [ "--cert", self.config["sbcert"] ]
    cmd += [ "--output", out.path ]
    cmd += [ infile.path ]

    self.do(cmd)

    out.signed = True

    return out


