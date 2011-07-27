Introduction
============

Credoscript is an Application Programming Interface (API) for the CREDO database.

Installation
------------

Software requirements
~~~~~~~~~~~~~~~~~~~~~
Credoscript is written in the `Python <http://www.python.org/>`_ programming language
and tested with versions 2.6 and 2.7. CREDO uses PostgreSQL as relational database
management system (RDBMS) so a Python driver for PostgreSQL is required to connect
to the database. PsycoPg2 can be installed on Debian-based systems with::

    $ sudo apt-get install python-psycopg2

It also requires `SQLAlchemy <http://www.sqlalchemy.org/>`_ version 0.7 or higher
for object-relational mapping (ORM) purposes.

Obtaining the source code
~~~~~~~~~~~~~~~~~~~~~~~~~
The source code for credoscript can be obtained by either downloading a source package
from the `Bitbucket <https://bitbucket.org/aschreyer/credoscript>`_ repository or
by cloning it with::

    $ hg clone https://aschreyer@bitbucket.org/aschreyer/credoscript

The directory containing the credoscript source code should be added to the ``$PYTHONPATH``
environment variable.

Configuring credoscript
~~~~~~~~~~~~~~~~~~~~~~~
The connections settings inside the default configuration file ``config-default.json``
have to be changed.


Testing the installation
~~~~~~~~~~~~~~~~~~~~~~~~
.. code-block:: python

   from credoscript import *

Documentation
-------------
This documentation is available from http://credoscript.readthedocs.org.

License
-------
Credoscript is released under the `MIT License <http://en.wikipedia.org/wiki/MIT_License>`_.