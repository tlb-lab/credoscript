from sqlalchemy.orm import backref, relationship

from credoscript import Base, schema
from credoscript.mixins import PathMixin, ResidueMixin

class Saccharide(Base, PathMixin, ResidueMixin):
    '''
    Represents a PDB saccharide Residue.

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
    their names, e.g. Saccharide['C']. Returns a list due to atoms with
    possible alternate locations.
    '''
    __tablename__ = '%s.saccharides' % schema['credo']
    
    Residue = relationship("Residue",
                           primaryjoin="Residue.residue_id==Saccharide.residue_id",
                           foreign_keys="[Residue.residue_id]", uselist=False, innerjoin=True,
                           backref=backref('Saccharide', uselist=False, innerjoin=True))