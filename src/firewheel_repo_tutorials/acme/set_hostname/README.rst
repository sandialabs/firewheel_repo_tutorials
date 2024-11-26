.. _acme.set_hostname_mc:

#################
acme.set_hostname
#################

This is a tutorial Model Component which is a partial implementation of the :ref:`acme-tutorial`.
Generally, this MC helps reset the hostname for each Ubuntu server.


**Attribute Provides:**
    * ``hostnames``

**Attribute Depends:**
    * ``acme_topology``

**Model Component Dependencies:**
    * :ref:`base_objects_mc`
    * :ref:`linux.ubuntu1604_mc`

**VM Resources:**
    * ``set_hostname.py``

******
Plugin
******

.. automodule:: acme.set_hostname_plugin
    :members:
    :undoc-members:
    :special-members:
    :private-members:
    :show-inheritance:
    :exclude-members: __dict__,__weakref__,__module__

