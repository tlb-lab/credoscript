**********************
Anatomy of credoscript
**********************

Introduction
============

|credoscript| is the |CREDO| database Application Programming Interface (API) developed
to facilitate analysis of the stored data by simplifying access to the database,
enabling scripting and integration of other useful Python modules and functions.
The Object-relational mapping (ORM) capabilities are implemented with the help of
SQLAlchemy (http://www.sqlalchemy.org), a Python SQL Toolkit and Object Relational
Mapper.

Basic concepts
==============

There are two kinds of objects fundamental to credoscript, namely **models** and
**adaptors**.

Models
------

A model in |credoscript| is simply a class mapped against a table, turning the
column values into attributes of a class instance. In addition, relationships to
other objects in |CREDO| are attributes as well.

Relationships
^^^^^^^^^^^^^

.. note::
   Relationship attributes of a model are always in CamelCase in |credoscript| to
   distinguish them from other attributes such as column data.

Adaptors
--------

An adaptor in credoscript is simply a class to fetch objects of the adaptor type
with methods that take parameters that will be used to query the database. This
approach has the advantage that users do not need to worry about constructing ORM
or SQL queries, although more advanced users can still use the ``session.query()``
method to compile their own queries.

BinaryExpressions
^^^^^^^^^^^^^^^^^

Extensions
==========