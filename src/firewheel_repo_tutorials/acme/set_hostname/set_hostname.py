#!/usr/bin/env python3

import sys
from abc import ABCMeta, abstractmethod
from platform import system
from subprocess import call


class SetHostname(object):
    """VM Resource used for setting system hostnames"""

    __metaclass__ = ABCMeta

    def run(self, fqdn):
        """
        The VM resource run method.

        Arguments:
            fqdn (str): The hostname for the system.
        """
        self.fqdn = fqdn.replace("_", "-")
        self.hostname = self.fqdn.split(".")[0]

        print("[hostname] setting hostname")
        self.set_hostname()

        print("[hostname] done")

    @abstractmethod
    def set_hostname(self):
        """Unused abstract method"""
        pass


class SetHostnameLinux(SetHostname):
    """VM Resource used for setting system hostnames"""

    def set_hostname(self):
        """Set the hostname for a Linux system."""
        # On Linux systems, overwrite /etc/hostname and then run the
        # hostname command
        with open("/etc/hostname", "w", encoding="utf-8") as f:
            f.write("%s\n" % self.hostname)

        call(["/bin/hostname", self.hostname])

        # Finally fix /etc/hosts
        call(
            [
                "/bin/sed",
                "-i",
                "s/ubuntu/%s %s/" % (self.fqdn, self.hostname),
                "/etc/hosts",
            ]
        )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Unable to set hostname. A hostname must be provided!")

    platform = system()
    if platform == "Linux":
        shn = SetHostnameLinux()

    shn.run(sys.argv[1])
