.. _tutorials.simple_server_mc:

#######################
tutorials.simple_server
#######################

This is a tutorial Model Component which is an implementation of the :ref:`simple-server-tutorial`.
Generally, this MC creates a Python web server and a number of clients which pull the files.
Each of the clients have a random delay on their network link.


**Attribute Provides:**
    * ``topology``



**Attribute Depends:**
    * ``graph``


**Model Component Dependencies:**
    * :ref:`base_objects_mc`
    * :ref:`linux.ubuntu1604_mc`


******
Plugin
******

.. automodule:: tutorials.simple_server_plugin
    :members:
    :undoc-members:
    :special-members:
    :private-members:
    :show-inheritance:
    :exclude-members: __dict__,__weakref__,__module__


*****************
Available Objects
*****************

.. automodule:: tutorials.simple_server
    :members:
    :undoc-members:
    :special-members:
    :private-members:
    :show-inheritance:
    :exclude-members: __dict__,__weakref__,__module__

