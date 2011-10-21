************************
Visualisation with PyMOL
************************

The |credoscript| API can be used to visualise structures and interactions in PyMOL.

Getting Started
---------------

PyMOL installation
~~~~~~~~~~~~~~~~~~

PyMol must be installed on your system. The software can be downloaded from the `PyMOL website <http://www.pymol.org/>`_ for free under an educational license, for a fee for a personal or commercial license. PyMOL is open source, and can be compiled from the freely available source code. More information on installation can be found on the `PyMOL wiki <http://www.pymol.org/>`_.

Running PyMOL
~~~~~~~~~~~~~

To use PyMOL with |credoscript|, PyMOL must be started with the "-R" flag to run while listening for commands using an XML-RPC server::

    $ pymol -R

Providing a PDB directory
~~~~~~~~~~~~~~~~~~~~~~~~~

PDB files to be loaded into PyMOL via |credoscript| are sourced locally. A directory must be provided in config.json in the |credoscript| directory:

.. code-block:: javascript

    "directory":
        {
            "pdb": "[path to PDB store...]"
        },


Using |credoscript| with PyMOL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

|credoscript| must be imported as follows:

.. code-block:: python

   from credoscript.pymol import *

All of the API features are available when importing as above.

Loading structures
------------------

CREDO biomolecules can be loaded into PyMOL via the API. Please note, biomolecules can not be loaded unless the PyMOL XML-RPC server is running and the PDB store is specified (see sections above).

Biomolecules are loaded into the PyMOL viewer using the Biomolecule object's load() method:

.. code-block:: python

   from credoscript.pymol import *
   
   s = StructureAdaptor().fetch_by_pdb("10gs")
   b = s.Biomolecules[1]
   b.load()
   # Structure loads in PyMOL window

Visualising ligand interactions
-------------------------------

Contacts to ligands in a biomolecule can be visualised using API calls via Ligand objects, using the show_contacts() method:

.. code-block:: python

   from credoscript.pymol import *
   
   s = StructureAdaptor().fetch_by_pdb("10gs")
   b = s.Biomolecules[1]
   b.load()
   
   l = b.Ligands[0]
   l.show_contacts()

Visualising protein-protein interactions
----------------------------------------

The same principle applies as with visualising ligand interactions:

.. code-block:: python

   from credoscript.pymol import *
   
   s = StructureAdaptor().fetch_by_pdb("10gs")
   b = s.Biomolecules[1]
   b.load()
   
   i = b.Interfaces[0]
   i.show_contacts()
