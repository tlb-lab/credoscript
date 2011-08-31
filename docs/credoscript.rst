**********************
Anatomy of credoscript
**********************

Introduction
============

Basic concepts
==============

There are two kinds of objects fundamental to credoscript, namely *models* and
*adaptors*.

Models
------

Relationships
^^^^^^^^^^^^^

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