****************************
Short introduction to Python
****************************

Overview
========

|Python| is a powerful programming language which "`combines remarkable power
with very clear syntax <http://docs.python.org/faq/general#what-is-python>`_".
Python is interpreted, which means that rather than compiling code into an
executable file, each line of code is read by the |Python| interpreter program,
which then executes the code. Interpretation confers the advantage of interactive
programming, line by line, in addition to running saved scripts, which is useful
for using the |credoscript| application programming interface (API) interactively
to explore structures and interactions or to conduct larger analyses in batch.


Installation
============

Platform-specific installation instructions can be followed from the `Python
documentation <http://docs.python.org/using/index.html>`_.

IPython
=======

`IPython <hhttp://ipython.org/>`_ is a powerful interactive |Python| shell and
is the recommended way to explore |credoscript|. The most useful feature of
|IPython| is tab completion, allowing you to see the functionality of the
different objects (e.g. Structures, Biomolecules, Ligands) in |credoscript|.

Advice
======

This introduction will attempt to introduce very briefly the key Python concepts
required for the use of |credoscript|. However, with respect to learning Python,
much more comprehensive tutorials exist, which will provide a much better understanding of
|Python| and how you can better use it for using |credoscript|. Some recommended
tutorials are referenced at the end of this page.

Python 101 for |credoscript|
============================

Prompt
------

In code examples, >>> indicates that it's something you would type in at an interactive
Python prompt. Any output is not preceeded by >>>. For example:

.. code-block:: python

   >>> 1 + 1
   2
   
In some examples demonstrating the syntax of the language, >>> may not be
included.
   
Objects
-------

Everything in Python is an **object**. All this means is that anything in Python
has the properties of any object in the real world, namely:
    
    - Things about it: in |Python|, these are called **attributes**
    - Things it can do: in |Python|, these are called **methods**

Relevant objects in |credoscript| are, for example, Structures, Biomolecules,
Interfaces, Ligands, Residues, Peptides (a single protein residue) and Atoms.
Behind the scenes, |credoscript| maps these objects to data in the |CREDO|
database. Attributes that belong to each object, such a Structure's
PDB code, are pulled in from the database. Some attributes may be accessed by a
method instead, for example a Ligand's "get_buried_surface" method.

Dot notation
------------

For an object, such as a car in the real world or a  Structure in |credoscript|
we have a way of saying "this attribute or method belongs to this object". In
English we say "a car has a steering wheel"; in Python, we say Object.attribute
or Object.method. Simply put, a dot indicates ownership. This makes sense if we
consider:

.. code-block:: python

   Biomolecule.Ligands
   
or

.. code-block:: python

   Ligand.get_contacts()

The Ligands attribute belongs to a Biomolecule, just as the get_contacts() method
belongs to a Ligand.

import x, or from x import y
----------------------------

The relevant lines in the case of |credoscript| are:

.. code-block:: python

   >>> from credoscript import *
   
and

.. code-block:: python

   >>> from credoscript.pymol import *
   
Notice how the dot notation is used again, but this time with reference to a
Python **package**, a collection of files (**modules**) containing code from which
all of the functionality can be gleaned without having the understand how it works
inside (for example, |credoscript|). When using the PyMOL API in |credoscript|, the
dot notation says in this case that the pymol module belongs to the |credoscript|
package. By importing everything in |credoscript| using from credoscript import \*,
you don't have to refer to every object by dot notation as in:

.. code-block:: python

   credoscript.Structure
   
and can instead simply use

.. code-block:: python

   Structure
   
Comments
--------

A **comment** is ignored by the Python interpreter. A # character starts a comment,
which continues to be a comment until the end of the line:

.. code-block:: python

   >>> 1 + 1 # I am ignored and can be used to document code
   2


Variables
---------

A **variable** is a name referring to an object. The object could be a number or a
string (essentially a string is text, it is a sequence of characters enclosed in
quotation marks such as "Hello!"), or it could be something more custom like
an object in |credoscript|. You assign an object to a variable with a name of
your choosing using "=", the **assignment operator**. Some simple examples:

.. code-block:: python

   >>> i = 1
   >>> i
   1
   >>> i + i
   2
   >>> i * 4
   4
   >>> h = "Hello"
   >>> h
   'Hello'
   >>> print h + "World!"
   HelloWorld!

Notice how if you submit the variable name alone, Python will return the object,
be it a number, a string or, for example, the text representation of a more
complex object such as a Structure, as you can see above. This example also introduces print,
which will print out a string to the console.

When fetching an object, such as a Structure, in |credoscript|, it is best to assign
it to a variable:

.. code-block:: python

   >>> from credoscript import *
   >>> s = StructureAdaptor().fetch_by_pdb("1XKK") # Don't worry about how this works yet!
   >>> s
   <Structure(1XKK)>
   
Don't worry yet about how the specific example works, just remember that you can assign an
object to any name of your choosing using "=".

You may also have noticed that the "+" operator can be used in different contexts for
addition and concatenation. Operators worth knowing about in Python include:

    - \+ for addition and concatenation
    - \- for subtraction
    - \* for multiplication
    - / for division
    - = for assignment
    - == for comparison (x == y resolves to True or False)

Referencing an object or method vs calling it
---------------------------------------------

For objects and their methods, Python distinguishes between you referring to the
object or method itself and actually creating the object/using the method. For all
intents and purposes, all this means is that you'll get a funny response if you
try to create an object or use a method without *parentheses* (). Parentheses
tell Python: "create or call this, rather than just refer to it":

.. code-block:: python

   >>> l = LigandAdaptor # An **adaptor** is a special object in |credoscript| used purely to fetch another object
   >>> l
   <class 'credoscript.adaptors.ligandadaptor.LigandAdaptor'>
   >>> # This hasn't made us a LigandAdaptor object: rather it has returned the LigandAdaptor **class**. A class is simply a blueprint for an object. An actual object must be created from a class by calling with parentheses ()
   >>> l = LigandAdaptor() 
   <credoscript.adaptors.ligandadaptor.LigandAdaptor object at 0x391ac10>
   >>> # Notice how an **object** was returned this time instead of a **class**.
   >>> lig = l.fetch_by_ligand_id
   >>> lig
   <bound method LigandAdaptor.fetch_by_ligand_id of <credoscript.adaptors.ligandadaptor.LigandAdaptor object at 0x391ac10>>
   >>> # We didn't fetch a ligand as we expected: we must call the method
   >>> lig = l.fetch_by_ligand_id(1) # Parentheses when calling a method or creating an object may contain parameters; in this case, a ligand id
   >>> lig
   <Ligand(A 210 VWW)>
   >>> # This time we got our ligand object!

Data structures
---------------

There are a few ways of storing data in Python which are important to be aware of
for the use of |credoscript|. They are summarised below:

**List**

A list is a sequence of objects or variables which refer to objects. The syntax for
lists is square bracket pairs [], which contain the items in the list separated by commas.

Looks like: ["Text", 1, <Structure(1XKK)>, ligand] (ligand is in this case a variable)

Can contain: Pretty much anything

Can be modified: Yes; objects in a list can be edited

Lists are **ordered** and objects can be accessed from within a list by referring to
the number in the sequence at which it resides using the following syntax:

.. code-block:: python

   >>> mylist = ["Hello", "Hi", "Goodbye"]
   >>> mylist[0]
   'Hello'
   >>> mylist[1]
   'Hi'
   >>> mylist[2] = "Hello again"
   >>> mylist[2]
   'Hello again'
   
Lists are **zero-indexed**, meaning that the count starts at zero.

**Tuple**

Like a list, but items can't be modified. Items are comma separated as in lists,
but are contained in parentheses. However, items are still accessed using the square
brackets notation:

.. code-block:: python

   >>> mytuple = ["Bonjour", "Hallo", "Au revoir"]
   >>> mytuple[0]
   'Bonjour'
   >>> mytuple[1]
   'Hallo'
   >>> mylist[2] = "Note to self: learn more languages"
   TypeError: 'tuple' object does not support item assignment
   
**Dictionary**

Instead of an ordered sequence of values, dictionaries store values as key-value
pairs, where a key can be used to access a value. A Python dictionary key can
be any **immutable** object, i.e. an object which can not be modified, such as
a number, or a literal string. However, dictionary values can be accessed by key and modified.
A dictionary is unordered, additional keys and values can be added after the
dictionary object is created. Dictionaries are notated by curly braces {}, and
accessed by the same square bracket notation as the other data structures:

.. code-block:: python

   >>> mydict = {"key": "value", "key2": 24, 15: "value3", "structure of interest": <Structure(1XKK)>}
   >>> mydict["key2"]
   24
   >>> mydict[15] = 86
   >>> mydict
   {15: 86, 'key': 'value', 'key2': 24, 'structure of interest': <Structure(1XKK)>}
   >>> mydict["new key"] = "new value" # Adding a new key-value pair by assigning it
   >>> mydict
   {15: 86, 'key': 'value', 'key2': 24, 'new key': 'new value', 'structure of interest': <Structure(1XKK)>}


Brief return to dot notation: chaining
--------------------------------------

A knowledge of accessing items in lists is a prerequisite for a |credoscript| example
of another feature of dot notation: dots can be chained where there is a
hierarchy of ownership, meaning you can get to the object you want faster:

.. code-block:: python

   >>> i = StructureAdaptor().fetch_by_pdb("10GS").Biomolecules[1].Interfaces[0]
   >>> i
   <Interface(1 2)>
   
Very powerful! Biomolecules is a dictionary, with the first assembly's key being 1.
Interfaces is a list, so the first interface is index 0. Putting these together, we
get straight from fetching a single Structure object using a StructureAdaptor object
to accessing its first Biomolecule assembly, and from within that assembly accessing the
first listed Interface object. Interface object attributes and methods can then be utilised in
analyses.

Using IPython tab completion
----------------------------

The principle advantage of using the IPython shell is tab-completion, which means you
don't have to remember the names of attributes and methods; everything becomes
self explanatory:

.. code-block:: python

     In [1]: from credoscript import *
     
     In [2]: s = St
     StandardError     StopIteration     Structure         StructureAdaptor  
     
     In [2]: s = Str
     Structure         StructureAdaptor  
     
     In [2]: s = StructureAdaptor().fetch_by_pdb("10GS")
     
     In [3]: s.
     s.Biomolecules         s.__init__             s.__subclasshook__     s.method
     s.XRefs                s.__iter__             s.__weakref__          s.num_biomolecules
     s.__class__            s.__le__               s._data                s.pdb
     s.__delattr__          s.__lt__               s._entity_id           s.ph
     s.__dict__             s.__module__           s._meta                s.r_factor
     s.__doc__              s.__ne__               s._pkey                s.r_free
     s.__eq__               s.__new__              s._sa_class_manager    s.release_date
     s.__format__           s.__reduce__           s._sa_instance_state   s.resolution
     s.__ge__               s.__reduce_ex__        s.abstracts            s.structure_id
     s.__getattribute__     s.__repr__             s.authors              s.title
     s.__getitem__          s.__setattr__          s.deposition_date      
     s.__gt__               s.__sizeof__           s.dpi                  
     s.__hash__             s.__str__              s.dpi_theoretical_min  
     
     In [3]: s.Biomolecules
     Out[3]: {1: <Biomolecule(1)>}
     
     In [4]: b = s.Biomolecules[1]
     
     In [5]: b.
     b.AromaticRings               b.__init__                    b._meta
     b.Atoms                       b.__iter__                    b._pkey
     b.Chains                      b.__le__                      b._sa_class_manager
     b.Interfaces                  b.__lt__                      b._sa_instance_state
     b.Ligands                     b.__module__                  b.assembly_serial
     b.Structure                   b.__ne__                      b.assembly_type
     b.__class__                   b.__new__                     b.biomolecule_id
     b.__delattr__                 b.__reduce__                  b.conformational_state_bm
     b.__dict__                    b.__reduce_ex__               b.get_atom_ring_interactions
     b.__doc__                     b.__repr__                    b.get_peptides
     b.__eq__                      b.__setattr__                 b.get_residues
     b.__format__                  b.__sizeof__                  b.get_ring_interactions
     b.__ge__                      b.__str__                     b.get_water
     b.__getattribute__            b.__subclasshook__            b.num_atoms
     b.__getitem__                 b.__weakref__                 b.num_chains
     b.__gt__                      b._data                       b.num_ligands
     b.__hash__                    b._entity_id                  b.structure_id
     
     In [5]: b.Chains
     Out[5]: {u'A': <Chain(A)>, u'B': <Chain(B)>}
     
     In [6]: b.Chains["A"]
     Out[6]: <Chain(A)>
     
     In [7]: c = b.Chains["A"]
     
     In [8]: c
     Out[8]: <Chain(A)>
     
     In [9]: c.
     c.Biomolecule             c.__le__                  c._sa_instance_state
     c.ProtFragments           c.__lt__                  c.biomolecule_id
     c.Residues                c.__module__              c.chain_id
     c.XRefs                   c.__ne__                  c.chain_length
     c.__class__               c.__new__                 c.chain_seq_md5
     c.__delattr__             c.__reduce__              c.chain_type
     c.__dict__                c.__reduce_ex__           c.get_contacts
     c.__doc__                 c.__repr__                c.get_disordered_regions
     c.__eq__                  c.__setattr__             c.get_nucleotides
     c.__format__              c.__sizeof__              c.get_peptides
     c.__ge__                  c.__str__                 c.get_residue_sifts
     c.__getattribute__        c.__subclasshook__        c.has_disordered_regions
     c.__getitem__             c.__weakref__             c.is_at_identity
     c.__getslice__            c._data                   c.pdb_chain_asu_id
     c.__gt__                  c._entity_id              c.pdb_chain_id
     c.__hash__                c._meta                   c.seq
     c.__init__                c._pkey                   c.title
     c.__iter__                c._sa_class_manager
     

Using tab completion, you can see everything an object has to offer.
An important note: methods/attributes beginning with an underscore "_" or two
underscores "__" are part of the object's internal **magic** and should not
be used directly.

More on Python
==============

This introduction explains only briefly the core concepts needed to understand how to
use Python in the context of |credoscript|. There is much more to the language
and by learning from the ground up, it is much easier to take advantage of the power
of |credoscript| and other tools. |Python| is popular in the scientific community
and is widely applied in scientific computing. Many tutorials and references are available online
if you would like to learn more:

`Python Beginners Guide <http://wiki.python.org/moin/BeginnersGuide>`_

`Dive into Python <http://www.diveintopython.net/>`_: For experienced programmers

Learning to use |credoscript|
=============================

The above quick tutorial gives you enough background on Python to learn how to
exploit the functionality of |credoscript|. To get stuck in straight away,
it is recommended to read :doc:`Objects in credoscript <credo-objects>` followed
by :doc:`Anatomy of credoscript <credoscript>`. These pages will put the above
explanations in the context of |credoscript| so that you can use the data extraction
and analysis functionality in |credoscript| effectively.
