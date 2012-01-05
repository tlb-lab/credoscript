from sqlalchemy.orm import backref, relationship
from sqlalchemy.orm.collections import attribute_mapped_collection

from credoscript import Base
from credoscript.mixins import PathMixin

class Biomolecule(Base, PathMixin):
    '''
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
    AromaticRings : list
        All AromaticRings identified in this Biomolecule.
    Atoms : list
        All Atoms of this Biomolecule.
    Chains : dict
        Dictionary in the form {pdb_chain_id: Chain} containing all Chains that
        have this `Biomolecule` as parent.
    Interfaces : list
        Protein-Protein Interfaces that exist between the polypeptide chains of
        this Biomolecule.
    Ligands : list
        List of `Ligand` objects that have this `Biomolecule` as parent
    Structure : Structure
        Parent of this Biomolecule, i.e. the PDB entry itself.

    See Also
    --------
    BiomoleculeAdaptor : Fetch Biomolecules from the database.

    Notes
    -----

    '''
    __tablename__ = 'credo.biomolecules'
    
    Chains = relationship("Chain",
                          collection_class=attribute_mapped_collection("pdb_chain_id"),
                          primaryjoin="Chain.biomolecule_id==Biomolecule.biomolecule_id",
                          foreign_keys="[Chain.biomolecule_id]", uselist=True, innerjoin=True,
                          backref=backref('Biomolecule', uselist=False, innerjoin=True))
    
    Interfaces = relationship("Interface",
                              primaryjoin="Interface.biomolecule_id==Biomolecule.biomolecule_id",
                              foreign_keys="[Interface.biomolecule_id]", uselist=True, innerjoin=True,
                              backref=backref('Biomolecule', uselist=False, innerjoin=True))
    
    Grooves = relationship("Groove",
                           primaryjoin="Groove.biomolecule_id==Biomolecule.biomolecule_id",
                           foreign_keys="[Groove.biomolecule_id]", uselist=True, innerjoin=True,
                           backref=backref('Biomolecule', uselist=False, innerjoin=True))
    
    Ligands = relationship("Ligand",
                           primaryjoin="Ligand.biomolecule_id==Biomolecule.biomolecule_id",
                           foreign_keys="[Ligand.biomolecule_id]", uselist=True, innerjoin=True,
                           backref=backref('Biomolecule', uselist=False, innerjoin=True))
    
    AromaticRings = relationship("AromaticRing",
                                 primaryjoin="AromaticRing.biomolecule_id==Biomolecule.biomolecule_id",
                                 foreign_keys="[AromaticRing.biomolecule_id]",
                                 uselist=True, innerjoin=True,
                                 backref=backref('Biomolecule', uselist=False, innerjoin=True))
    
    Atoms = relationship("Atom",
                         primaryjoin="Atom.biomolecule_id==Biomolecule.biomolecule_id",
                         foreign_keys="[Atom.biomolecule_id]", uselist=True, innerjoin=True,
                         backref=backref('Biomolecule', uselist=False, innerjoin=True)),
    
    
    def __repr__(self):
        '''
        '''
        return '<Biomolecule({self.assembly_serial})>'.format(self=self)

    def __getitem__(self, pdb_chain_id):
        '''
        '''
        return self.Chains.get(pdb_chain_id)

    def __iter__(self):
        '''
        '''
        return iter(self.Chains.values())

    def get_water(self, *expressions):
        '''
        '''
        return ResidueAdaptor().fetch_all_by_biomolecule_id(self.biomolecule_id, Residue.res_name=='HOH', *expressions)

    def get_residues(self, *expressions):
        '''
        '''
        return ResidueAdaptor().fetch_all_by_biomolecule_id(self.biomolecule_id, *expressions)

    def get_peptides(self, *expressions):
        '''
        '''
        return PeptideAdaptor().fetch_all_by_biomolecule_id(self.biomolecule_id, *expressions)

    def get_ring_interactions(self, *expressions):
        '''
        '''
        return RingInteractionAdaptor().fetch_all_by_biomolecule_id(self.biomolecule_id, *expressions)

    def get_atom_ring_interactions(self, *expressions):
        '''
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
        '''
        return AtomRingInteractionAdaptor().fetch_all_by_biomolecule_id(self.biomolecule_id, *expressions)

from .residue import Residue
from ..adaptors.peptideadaptor import PeptideAdaptor
from ..adaptors.residueadaptor import ResidueAdaptor
from ..adaptors.ringinteractionadaptor import RingInteractionAdaptor
from ..adaptors.atomringinteractionadaptor import AtomRingInteractionAdaptor
from ..adaptors.interfaceadaptor import InterfaceAdaptor
from ..adaptors.protfragmentadaptor import ProtFragmentAdaptor