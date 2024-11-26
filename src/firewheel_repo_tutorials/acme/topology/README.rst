.. _acme.topology_mc:

#############
acme.topology
#############

This is a tutorial Model Component which is a partial implementation of the :ref:`acme-tutorial`.
Generally, this MC creates a example corporate network.


**Attribute Provides:**
    * ``topology``
    * ``acme_topology``

**Attribute Depends:**
    * ``graph``


**Model Component Dependencies:**
    * :ref:`base_objects_mc`
    * :ref:`linux.ubuntu2204_mc`
    * :ref:`vyos.helium118_mc`

******
Plugin
******

.. automodule:: acme.topology_plugin
    :members:
    :undoc-members:
    :special-members:
    :private-members:
    :show-inheritance:
    :exclude-members: __dict__,__weakref__,__module__
