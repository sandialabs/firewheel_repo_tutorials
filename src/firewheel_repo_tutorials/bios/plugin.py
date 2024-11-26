from linux.ubuntu1604 import Ubuntu1604Server

from firewheel.control.experiment_graph import Vertex, AbstractPlugin


class Plugin(AbstractPlugin):
    """The basic example for modifying a VM's BIOS."""

    def run(self):
        """Create a single VM and add a custom BIOS for it."""
        bios_vm = Vertex(self.g, "bios-vm")
        bios_vm.decorate(Ubuntu1604Server)
        bios_vm.vm["bios"] = "bios.bin"
