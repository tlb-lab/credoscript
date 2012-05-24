# Introduction

**credoscript** is the **CREDO** database Application Programming Interface (API)
developed to facilitate analysis of the stored data by simplifying access to the
database, enabling scripting and integration of other useful Python modules and
functions. The Object-relational mapping (ORM) capabilities are implemented with
the help of SQLAlchemy, a Python SQL Toolkit and Object Relational Mapper.

# Installation

## Software requirements

**credoscript** is written in the [Python](http://www.python.org) programming language
and tested with versions 2.6 and 2.7. CREDO uses [PostgreSQL](http://www.postgresql.org)
as relational database management system (RDBMS) so a Python driver for PostgreSQL
is required to connect to the database. [Psycopg](http://www.initd.org/psycopg)
can be installed on Debian-based systems with

    $ sudo apt-get install python-psycopg2

or more generally with

    $ sudo pip install psycopg2

It also requires [SQLAlchemy](http://www.sqlalchemy.org) version 0.7 or higher
for object-relational mapping (ORM) purposes.

## Obtaining the source code

The source code for **credoscript** can be obtained by either downloading a source
package from the [Bitbucket](https://bitbucket.org/aschreyer/credoscript) repository
or by cloning it with

    $ hg clone https://bitbucket.org/aschreyer/credoscript

And switching to the stable branch:

    $ hg update stable

The directory containing the **credoscript** source code should be added to the
`$PYTHONPATH` environment variable.

## Configuring credoscript

The connection settings inside the default configuration file `config-default.json`
have to be changed and the file renamed to `config.json`.

# License

Credoscript is released under the [MIT License](http://en.wikipedia.org/wiki/MIT_License).