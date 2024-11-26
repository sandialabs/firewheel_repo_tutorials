from netaddr import IPNetwork
from base_objects import Switch
from vyos.helium118 import Helium118
from linux.ubuntu2204 import Ubuntu2204Server, Ubuntu2204Desktop

from firewheel.control.experiment_graph import Vertex, AbstractPlugin


class Plugin(AbstractPlugin):
    """acme.topology plugin documentation."""

    def run(self):
        """Run method documentation."""
        # Create an external-facing network and an iterator for that network.
        # The iterator will provide the next available netaddr.IPAddress for the given
        # network.
        self.external_network = IPNetwork("1.0.0.0/24")
        external_network_iter = self.external_network.iter_hosts()

        # Create an internal facing network
        internal_networks = IPNetwork("10.0.0.0/8")

        # Break the internal network into various subnets
        # https://netaddr.readthedocs.io/en/latest/tutorial_01.html#supernets-and-subnets
        self.internal_subnets = internal_networks.subnet(24)

        # Create the gateway and firewall
        firewall = self.build_front(next(external_network_iter))

        # Create an internal switch
        internal_switch = Vertex(self.g, name="ACME-INTERNAL")
        internal_switch.decorate(Switch)

        # Grab a subnet to use for connections to the internal switch
        internal_switch_network = next(self.internal_subnets)
        # Create a generator for the network
        internal_switch_network_iter = internal_switch_network.iter_hosts()

        # Connect the Firewall to the internal switch
        firewall.ospf_connect(
            internal_switch,
            next(internal_switch_network_iter),
            internal_switch_network.netmask,
        )

        # Create our first building
        building_1 = self.build_building(
            "building1",  # The name of the building
            next(self.internal_subnets),  # The building network
            num_hosts=3,  # The number of hosts for the building
        )

        # Connect the first building router to the internal switch.
        building_1.ospf_connect(
            internal_switch,
            next(internal_switch_network_iter),
            internal_switch_network.netmask,
        )

        # Create our second building
        building_2 = self.build_building(
            "building2",  # The name of the building
            next(self.internal_subnets),  # The building network
            num_hosts=3,  # The number of hosts for the building
        )

        # Connect the second building router to the internal switch.
        building_2.ospf_connect(
            internal_switch,
            next(internal_switch_network_iter),
            internal_switch_network.netmask,
        )

        # Build our data center
        self.build_datacenter(
            building_2,  # The building Vertex
            next(
                self.internal_subnets
            ),  # Add a network to connect the DC to the building
            next(self.internal_subnets),  # Add a network which is internal to the DC
        )

    def build_front(self, ext_ip):
        """Build the ACME infrastructure that is Internet-facing.

        This method will create the following topology::

                switch -- gateway -- switch -- firewall
            (ACME-EXTERNAL)         (GW-FW)

        Args:
            ext_ip (netaddr.IPAddress): The external IP address for the gateway
                (e.g. its Internet facing IP address).

        Returns:
            vyos.Helium118: The Firewall object.
        """

        # Build the gateway
        gateway = Vertex(self.g, "gateway.acme.com")
        gateway.decorate(Helium118)

        # Create the external switch
        ext_switch = Vertex(self.g, name="ACME-EXTERNAL")
        ext_switch.decorate(Switch)

        # Connect the gateway to the external switch
        gateway.connect(
            ext_switch,  # The "Internet" facing Switch
            ext_ip,  # The external IP address for the gateway (e.g. 1.0.0.1)
            self.external_network.netmask,  # The external subnet mask (e.g. 255.255.255.0)
        )

        # Build a switch to connect the gateway and firewall
        gateway_firewall_switch = Vertex(self.g, name="GW-FW")
        gateway_firewall_switch.decorate(Switch)

        # Build the firewall
        firewall = Vertex(self.g, "firewall.acme.com")
        firewall.decorate(Helium118)

        # Create a network and a generator for the network between
        # the gateway and firewall.
        gateway_firewall_network = next(self.internal_subnets)
        gateway_firewall_network_iter = gateway_firewall_network.iter_hosts()

        # Connect the gateway and the firewall to their respective switches
        # We will use ``ospf_connect`` to ensure that the OSPF routes are propagated
        # correctly (as we want to use OSPF as routing protocol inside of the ACME network).
        gateway.ospf_connect(
            gateway_firewall_switch,
            next(gateway_firewall_network_iter),
            gateway_firewall_network.netmask,
        )
        firewall.ospf_connect(
            gateway_firewall_switch,
            next(gateway_firewall_network_iter),
            gateway_firewall_network.netmask,
        )
        return firewall

    def build_building(self, name, network, num_hosts=1):
        """Create the building router and hosts.

        This is a single router with all of the hosts.
        Assuming that the building is called "building1" the topology will look like::

                switch ---- building1 ----- switch ------ hosts
            (ACME-INTERNAL)           (building1-switch)

        Args:
            name (str): The name of the building.
            network (netaddr.IPNetwork): The subnet for the building.
            num_hosts (int): The number of hosts the building should have.

        Returns:
            vyos.Helium118: The building router.
        """

        # Create the VyOS router which will connect the building to the ACME network.
        building = Vertex(self.g, name=f"{name}.acme.com")
        building.decorate(Helium118)

        # Create the building-specific switch
        building_sw = Vertex(self.g, name=f"{name}-switch")
        building_sw.decorate(Switch)

        # Create a generator for the building's network
        building_network_iter = network.iter_hosts()

        # Connect the building to the building Switch
        building.connect(building_sw, next(building_network_iter), network.netmask)

        # This redistribute routes for directly connected subnets to OSPF peers.
        # That is, enables these peers to be discoverable by the rest of the OSPF
        # routing infrastructure.
        building.redistribute_ospf_connected()

        # Create the correct number of hosts
        for i in range(num_hosts):
            # Create a new host which is a Ubuntu Desktop
            host = Vertex(
                self.g,
                name=f"{name}-host-{i}.acme.com",  # e.g. "building1-host-1.acme.com"
            )
            host.decorate(Ubuntu2204Desktop)

            # Connect the host to the building's switch
            host.connect(
                building_sw,  # The building switch
                next(building_network_iter),  # The next available building IP address
                network.netmask,  # The building's subnet mask
            )

        return building

    def build_datacenter(self, building, uplink_network, dc_network):
        """Create the data center.

        This is a single router with all of the servers::

           building2 ------ switch ------ datacenter ------ switch ------ servers
                     (building2-DC-switch)                (DC-switch)

        Args:
            building (vyos.Helium118): The Building router which contains the data center.
            uplink_network (netaddr.IPNetwork): The network to connect the DC to the building.
            dc_network (netaddr.IPNetwork): The network for the data center.
        """
        # Create a switch to connect the DC with the building
        building_dc_sw = Vertex(self.g, name=f"{building.name}-DC-switch")
        building_dc_sw.decorate(Switch)

        # Create the datacenter router
        datacenter = Vertex(self.g, name="datacenter.acme.com")
        datacenter.decorate(Helium118)

        # Create a generator for the building's network
        uplink_network_iter = uplink_network.iter_hosts()

        # Connect the building to the building-DC-switch
        building.ospf_connect(
            building_dc_sw, next(uplink_network_iter), uplink_network.netmask
        )

        # Connect the datacenter to the building-DC-switch
        datacenter.ospf_connect(
            building_dc_sw, next(uplink_network_iter), uplink_network.netmask
        )

        # Make the datacenter internal switch and connect
        datacenter_sw = Vertex(self.g, name="DC-switch")
        datacenter_sw.decorate(Switch)

        # Create a generator for the DC's network
        dc_network_iter = dc_network.iter_hosts()

        # Connect the DC to the internal switch
        datacenter.connect(datacenter_sw, next(dc_network_iter), dc_network.netmask)

        # This redistribute routes for directly connected subnets to OSPF peers.
        # That is, enables these peers to be discoverable by the rest of the OSPF
        # routing infrastructure.
        datacenter.redistribute_ospf_connected()

        # Make servers
        for i in range(3):
            # Create a new Ubuntu server and add connect it to the DC network switch
            server = Vertex(self.g, name=f"datacenter-{i}.acme.com")
            server.decorate(Ubuntu2204Server)
            server.connect(datacenter_sw, next(dc_network_iter), dc_network.netmask)
