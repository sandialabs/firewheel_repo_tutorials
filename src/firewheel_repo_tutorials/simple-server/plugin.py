import random

from base_objects import Switch
from tutorials.simple_server import SimpleClient, SimpleServer

from firewheel.control.experiment_graph import Vertex, AbstractPlugin


class Plugin(AbstractPlugin):
    """tutorials.simple_server plugin documentation.

    This Plugin creates a basic topology with a Server and several clients.
    The clients all have a random delay on their outbound connection.
    """

    def run(self, num_clients="1"):
        """Run method documentation.

        This method contains the primary logic for the Plugin.

        Arguments:
            num_clients (str): The number of clients in the topology. This should be
                convertible to an integer.

        Raises:
            TypeError: If the number of clients is not a valid integer.
            ValueError: If the number of clients is not a valid integer.
        """
        try:
            # Convert the number of clients to an integer
            num_clients = int(num_clients)
        except (TypeError, ValueError):
            print("The number of clients has to be a valid integer.")
            raise

        # Create the Server
        server = Vertex(self.g, name="Server")
        server.decorate(SimpleServer)

        # Create the switch
        switch = Vertex(self.g, name="Switch")
        switch.decorate(Switch)

        # Connect the server and the switch
        server_ip = "1.0.0.1"
        server.connect(
            switch,  # The Switch Vertex
            server_ip,  # The IP address for the server
            "255.255.255.0",  # The subnet mask for the IP address network
        )

        # Create all of our clients
        for i in range(num_clients):
            client = self.create_client(f"client-{i}", server_ip)

            delay = random.randint(1, 100)
            # Connect the client and the switch
            client.connect(
                switch,  # The Switch Vertex
                f"1.0.0.{i + 2}",  # The IP address for the client
                "255.255.255.0",  # The subnet mask for the IP address network
                delay=f"{delay}ms",
            )

    def create_client(self, name, server_ip):
        """Create a single client.

        Arguments:
            name (str): The name of the vertex.
            server_ip (str): The IP Address of the Server.

        Returns:
            tutorials.simple_server.SimpleClient: The newly created client.
        """
        client = Vertex(self.g, name=name)
        client.decorate(SimpleClient)
        client.grab_file(server_ip)
        return client
