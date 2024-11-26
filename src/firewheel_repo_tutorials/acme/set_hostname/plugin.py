from linux.ubuntu2204 import Ubuntu2204Server

from firewheel.control.experiment_graph import AbstractPlugin


class Plugin(AbstractPlugin):
    """ACME plugin to set hostnames for all VMs"""

    def run(self):
        """
        Find all Ubuntu servers and try to assign a new hostname to them
        using our custom VM resource.
        """
        for vm in self.g.get_vertices():
            if vm.is_decorated_by(Ubuntu2204Server):
                try:
                    hostname = vm.name.replace("building", "b", 1).replace(
                        "host", "ubuntu", 1
                    )
                except AttributeError:
                    print(f"Found VM without a name: {vm}")
                    continue

                vm.run_executable(-40, "set_hostname.py", hostname, vm_resource=True)
