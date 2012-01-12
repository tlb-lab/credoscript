from sqlalchemy.orm import backref, relationship
from sqlalchemy.orm.collections import attribute_mapped_collection

from credoscript import Base
from credoscript.mixins import PathMixin, ResidueMixin

class Peptide(Base, PathMixin, ResidueMixin):
    '''
    Represents a PDB polypeptide Residue.

    Attributes
    ----------
    residue_id : int
        Primary key.
    chain_id : int
        "Foreign key" of the parent Chain.
    res_name : str
        The PDB three-letter chemical component name / Three-letter amino acid code.
    one_letter_code : string
        The one-letter code of this amino acid.
    res_num : int
        The PDB residue number.
    ins_code : str
        The PDB insertion code.
    entity_type_bm : int
        Entity type bitmask containing six bits.

    Mapped attributes
    -----------------
    Rings : Query
        AromaticRings of this Residue in case is it aromatic.
    Atoms : Query
        Atoms of this Residue.
    XRefs : Query
        CREDO XRef objects that are associated with this Residue Entity.

    Notes
    -----
    The __getitem__ method is overloaded to allow accessing Atoms directly by
    their names, e.g. Residue['CA']. Returns a list due to atoms with
    possible alternate locations.
    '''
    __tablename__ = 'credo.peptides'    
    
    Residue = relationship("Residue",
                            primaryjoin="Residue.residue_id==Peptide.residue_id",
                            foreign_keys="[Residue.residue_id]", uselist=False, innerjoin=True,
                            backref=backref('Peptide', uselist=False, innerjoin=True))
    
    ResMap = relationship("ResMap",
                          primaryjoin="ResMap.res_map_id==Peptide.res_map_id",
                          foreign_keys = "[ResMap.res_map_id]",
                          uselist=False, innerjoin=True)
    
    @property
    def Contacts(self):
        '''
        '''
        return ContactAdaptor().fetch_all_by_residue_id(self.residue_id,
                                                        Atom.biomolecule_id==self.biomolecule_id,
                                                        dynamic=True)

from .atom import Atom
from ..adaptors.contactadaptor import ContactAdaptor