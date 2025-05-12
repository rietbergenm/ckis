modname = "layout/bls-type-2"
moddesc = """
BootLoader Specification type 2 compatible layout

Also known as the plain UKI layout; puts a unified kernel image in
$ESP/EFI/Linux. Bootloaders that support the specification can auto-discover
these uki's (e.g. systemd-boot).
"""

inputs =  { "uki" }


def fire(self):
    uki = self.copy(self.inputs["uki"])

    uki.path = self.esp / ("EFI/Linux/"
        f"{self.osrelease['ID']}-{self.name}-{self.kver}.efi")

    self.mkdir(self.esp / "EFI/Linux", parents=True)
    self.cp(self.inputs["uki"].path, uki.path)

    uki.installed = True

    return uki
