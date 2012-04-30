from sqlalchemy.orm import backref, relationship
from sqlalchemy.orm.collections import attribute_mapped_collection

from credoscript import Base
from credoscript.mixins import PathMixin

class Biomolecule(Base, PathMixin):
    """
    Represents a biological assembly of a PDB structure, henceforth known as
    'Biomolecule'.

    Attributes
    ----------
    biomolecule_id : int
        Primary key.
    structure_id: int
        Primary key of the parent structure.
    assembly_serial : int
        Serial number of the assembly - can be > 1 if asymmetric unit contains
        more than one biological assembly.
    assembly_type : str
        Assembly type of the biomolecule, e.g. Monomeric.
    num_chains : int
        Number of chains in biological assembly.
    num_ligands : int
        Number of ligands in biological assembly.
    num_atoms : int
        Number of atoms in biological assembly.

    Mapped Attributes
    -----------------
    Structure : Structure
        Parent of this Biomolecule, i.e. the PDB entry itself.
    Chains : Query
        Chains that have this Biomolecule as parent.
    ChainMap : dict
        Dictionary in the form {pdb_chain_id: Chain} containing all Chains that
        have this `Biomolecule` as parent.
    Interfaces : Query
        Protein-Protein Interfaces that exist between the polypeptide chains of
        this Biomolecule.
    Grooves : Query
        Protein-nucleic acid complexes grooves found in this Biomolecule.
    Ligands : Query
        Ligands that have this Biomolecule as parent.
    Residues : Query
        Residues of this Biomolecule.
    Peptides : Query    
        Peptides of this Biomolecule.
    AromaticRings : Query
        AromaticRings identified in this Biomolecule.
    Atoms : Query
        Atoms of this Biomolecule.

    See Also
    --------
    BiomoleculeAdaptor : Fetch Biomolecules from the database.

    Notes
    -----
    - The __getitem__ method is overloaded to allow indexing shortcuts in the form
      Biomolecule['A'] which return Chains.
    - Not all atoms and residues of a Biomolecule can be found in CREDO; only complete
      residues and their atoms that interact are stored.
    """
    __tablename__ = 'credo.biomolecules'
    
    Chains = relationship("Chain",
                          primaryjoin="Chain.biomolecule_id==Biomolecule.biomolecule_id",
                          foreign_keys="[Chain.biomolecule_id]",
                          uselist=True, innerjoin=True, lazy='dynamic',
                          backref=backref('Biomolecule', uselist=False, innerjoin=True))
    
    # map chain entities as dictionary in the form {<pdb chain id>: chain}
    ChainMap = relationship("Chain",
                            collection_class=attribute_mapped_collection("pdb_chain_id"),
                            primaryjoin="Chain.biomolecule_id==Biomolecule.biomolecule_id",
                            foreign_keys="[Chain.biomolecule_id]",
                            uselist=True, innerjoin=True)    
    
    Interfaces = relationship("Interface",
                              primaryjoin="Interface.biomolecule_id==Biomolecule.biomolecule_id",
                              foreign_keys="[Interface.biomolecule_id]",
                              uselist=True, innerjoin=True, lazy='dynamic',
                              backref=backref('Biomolecule', uselist=False, innerjoin=True))
    
    Grooves = relationship("Groove",
                           primaryjoin="Groove.biomolecule_id==Biomolecule.biomolecule_id",
                           foreign_keys="[Groove.biomolecule_id]",
                           uselist=True, innerjoin=True, lazy='dynamic',
                           backref=backref('Biomolecule', uselist=False, innerjoin=True))
    
    Ligands = relationship("Ligand",
                           primaryjoin="Ligand.biomolecule_id==Biomolecule.biomolecule_id",
                           foreign_keys="[Ligand.biomolecule_id]",
                           uselist=True, innerjoin=True, lazy='dynamic',
                           backref=backref('Biomolecule', uselist=False, innerjoin=True))
    
    Residues = relationship("Residue",
                            primaryjoin="Residue.biomolecule_id==Biomolecule.biomolecule_id",
                            foreign_keys="[Residue.biomolecule_id]",
                            uselist=True, innerjoin=True, lazy='dynamic',
                            backref=backref('Biomolecule', uselist=False, innerjoin=True))
    
    Peptides = relationship("Peptide",
                            primaryjoin="Peptide.biomolecule_id==Biomolecule.biomolecule_id",
                            foreign_keys="[Peptide.biomolecule_id]",
                            uselist=True, innerjoin=True, lazy='dynamic',
                            backref=backref('Biomolecule', uselist=False, innerjoin=True))  
    
    AromaticRings = relationship("AromaticRing",
                                 primaryjoin="AromaticRing.biomolecule_id==Biomolecule.biomolecule_id",
                                 foreign_keys="[AromaticRing.biomolecule_id]",
                                 uselist=True, innerjoin=True, lazy='dynamic',
                                 backref=backref('Biomolecule', uselist=False, innerjoin=True))  
    
    RingInteractions = relationship("RingInteraction",
                                     primaryjoin="RingInteraction.biomolecule_id==Biomolecule.biomolecule_id",
                                     foreign_keys="[RingInteraction.biomolecule_id]",
                                     uselist=True, innerjoin=True, lazy='dynamic',
                                     backref=backref('Biomolecule', uselist=False, innerjoin=True)) 
    
    Atoms = relationship("Atom",
                         primaryjoin="Atom.biomolecule_id==Biomolecule.biomolecule_id",
                         foreign_keys="[Atom.biomolecule_id]",
                         uselist=True, innerjoin=True, lazy='dynamic',
                         backref=backref('Biomolecule', uselist=False, innerjoin=True))
    
    
    def __repr__(self):
        """
        """
        return '<Biomolecule({self.assembly_serial})>'.format(self=self)

    def __getitem__(self, pdb_chain_id):
        """
        Used for quick indexing, e.g. Biomolecule['A'].
        """
        return self.ChainMap.get(pdb_chain_id)

    def __iter__(self):
        """
        """
        return iter(self.Chains)
        
    @property
    def AtomRingInteractions(self):
        """
        Returns all the interactions between an atom and an aromatic ring.

        Parameters
        ----------
        *expressions : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried Entities
        ----------------
        AtomRingInteraction, AromaticRing

        Returns
        -------
        contacts : list
            List of `AtomRingInteraction` objects.

         Examples
        --------
        >>> self.get_atom_ring_interactions()
        [<AtomRingInteraction(22271)>, <AtomRingInteraction(22272)>,
         <AtomRingInteraction(22273)>, <AtomRingInteraction(22274)>,
         <AtomRingInteraction(22275)>, <AtomRingInteraction(22276)>,
         <AtomRingInteraction(22277)>]
        """
        return AtomRingInteractionAdaptor().fetch_all_by_biomolecule_id(self.biomolecule_id,
                                                                        dynamic=True)

from .residue import Residue
from ..adaptors.residueadaptor import ResidueAdaptor
from ..adaptors.ringinteractionadaptor import RingInteractionAdaptor
from ..adaptors.atomringinteractionadaptor import AtomRingInteractionAdaptor