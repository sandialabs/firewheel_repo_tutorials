"""This module contains all necessary Model Component Objects for tutorials.simple_server."""

import os

from linux.ubuntu1604 import Ubuntu1604Server

from firewheel.control.experiment_graph import require_class


@require_class(Ubuntu1604Server)
class SimpleServer:
    """SimpleServer Class documentation."""

    def __init__(self):
        """Initialize the class by creating the file and serving it via Python."""
        self.configure_files_to_serve()

        # Start the web server at time=1
        # The server needs to run in the ``/opt`` directory because that is where the
        # file will be located.
        self.run_executable(
            1,  # The experiment time to run this program (e.g. 1 second after start).
            "bash",  # The name of the executable program to run.
            arguments="-c 'pushd /opt; python3 -m http.server; popd'",  # The arguments for the program.
        )

    def configure_files_to_serve(self, file_size=52428800):
        """
        Generate a file that is of size ``file_size`` (e.g. default of 50MB) and
        drop it on the VM.

        Args:
            file_size (int): The size of the file to create. By default is 52428800 (i.e. 50MB.
        """
        # Get the current executing directory
        current_module_path = os.path.abspath(os.path.dirname(__file__))

        # Create a path to the soon-to-be-created file
        filename = "file.txt"
        path = os.path.join(current_module_path, "vm_resources", filename)

        # Generate the random data which will fill the file
        random_bytes = os.urandom(file_size)

        # Write the file to disk
        with open(path, "wb") as fout:
            fout.write(random_bytes)

        # Drop the new file onto the VM.
        self.drop_file(
            -5,  # The experiment time to add the content. (i.e. during configuration)
            f"/opt/{filename}",  # The location on the VM of the file to drop
            filename,  # The filename of the newly created file on the physical host.
        )


@require_class(Ubuntu1604Server)
class SimpleClient:
    """SimpleClient Class documentation."""

    def __init__(self):
        """Used init method"""
        pass

    def grab_file(self, server_ip):
        """
        Add a curl format to the VM and then the cURL command to grab the file.
        The custom format will help output the time of the download in JSON format
        for easy analysis.
        """
        # Drop the cURL format string
        self.drop_content(
            -5,  # The experiment time to add the content. (i.e. during configuration)
            "/opt/curl_format.txt",  # The location on the VM of the file
            '{"time":"%{time_total}"}\\n',  # The content to add to the file.
        )

        # Run cURL command
        self.run_executable(
            10,  # The experiment time to run this program (e.g. 10 seconds after start).
            "/usr/bin/curl",  # The name of the executable program to run.
            arguments=f'-w "@/opt/curl_format.txt" -O {server_ip}:8000/file.txt',
        )
