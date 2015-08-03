from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property

from credoscript import Base, BaseQuery, schema
from credoscript.support import interactiontypes as it

class Contact(Base):
    '''
    Represents a Contact entity from CREDO.

    Attributes
    ----------
    contact_id : int
        Primary key.
    '''
    __table__ = Base.metadata.tables['%s.contacts' % schema['credo']]
    
    AtomBgn  = relationship("Atom", query_class=BaseQuery,
                            primaryjoin="and_(Atom.atom_id==Contact.atom_bgn_id, Atom.biomolecule_id==Contact.biomolecule_id)", # PARTITION CONSTRAINT-EXCLUSION
                            foreign_keys="[Atom.atom_id, Atom.biomolecule_id]",
                            uselist=False, innerjoin=True,
                            backref=backref('ContactsBgn', uselist=True,
                                            innerjoin=True, lazy='dynamic'))
    
    AtomEnd = relationship("Atom", query_class=BaseQuery,
                           primaryjoin="and_(Atom.atom_id==Contact.atom_end_id, Atom.biomolecule_id==Contact.biomolecule_id)", # PARTITION CONSTRAINT-EXCLUSION
                           foreign_keys="[Atom.atom_id, Atom.biomolecule_id]",
                           uselist=False, innerjoin=True,
                           backref=backref('ContactsEnd', uselist=True,
                                            innerjoin=True, lazy='dynamic'))    
    
    def __repr__(self):
        '''
        '''
        return "<Contact(%i, %i)>" % (self.atom_bgn_id, self.atom_end_id)

    def _bm_bitwise_all(self, x):
        """
        """
        return self.structural_interaction_type_bm & x == x

    @classmethod
    def _bm_bitwise_all_exp(cls, x):
        """
        """
        return cls.structural_interaction_type_bm.op('&')(x) == x

    def _bm_bitwise_all_asym(self, x, y):
        """
        """
        return self.structural_interaction_type_bm & x == x or self.structural_interaction_type_bm & y == y

    @classmethod
    def _bm_bitwise_all_asym_exp(cls, x, y):
        """
        """
        return (cls.structural_interaction_type_bm.op('&')(x) == x) | (cls.structural_interaction_type_bm.op('&')(y) == y)
    
    def _bm_bitwise_any(self, x):
        """
        """
        return self.structural_interaction_type_bm & x > 0

    @classmethod
    def _bm_bitwise_any_exp(cls, x):
        """
        """
        return cls.structural_interaction_type_bm.op('&')(x) > 0
    
    @hybrid_property
    def is_lig_lig(self):
        """
        Returns True if the contact is between two ligand atoms.
        """
        return self._bm_bitwise_all(it.LIG_LIG)

    @is_lig_lig.expression
    def is_lig_lig(cls):
        """
        Returns an SQLAlchemy boolean expression to test if a contact is between
        two ligand atoms.
        """
        return cls._bm_bitwise_all_exp(it.LIG_LIG)
    
    @hybrid_property
    def is_pro_dna(self):
        """
        Returns True if the contact is between a polypeptide and an DNA atom.
        """
        return self._bm_bitwise_all_asym(it.PRO_DNA, it.DNA_PRO)

    @is_pro_dna.expression
    def is_pro_dna(cls):
        """
        Returns an SQLAlchemy boolean expression to test if a contact is between
        a polypeptide and an DNA atom.
        """
        return cls._bm_bitwise_all_asym_exp(it.PRO_DNA, it.DNA_PRO)
    
    @hybrid_property
    def is_pro_lig(self):
        """
        Returns True if the contact is between a polypeptide and a ligand atom.
        """
        return self._bm_bitwise_all_asym(it.PRO_LIG, it.LIG_PRO)

    @is_pro_lig.expression
    def is_pro_lig(cls):
        """
        Returns an SQLAlchemy boolean expression to test if contact is between a
        polypeptide and a ligand atom.
        """
        return cls._bm_bitwise_all_asym_exp(it.PRO_LIG, it.LIG_PRO)
    
    @hybrid_property
    def is_pro_pro(self):
        """
        Returns True if the contact is between two polypeptide atoms.
        """
        return self._bm_bitwise_all(it.PRO_PRO)

    @is_pro_pro.expression
    def is_pro_pro(cls):
        """
        Returns an SQLAlchemy boolean expression to test if contact is between two
        polypeptide atoms.
        """
        return cls._bm_bitwise_all_exp(it.PRO_PRO)
    
    @hybrid_property
    def is_pro_rna(self):
        """
        Returns True if the contact is between a polypeptide and an RNA atom.
        """
        return self._bm_bitwise_all_asym(it.PRO_RNA, it.RNA_PRO)

    @is_pro_rna.expression
    def is_pro_rna(cls):
        """
        Returns an SQLAlchemy boolean expression to test if a contact is between
        a polypeptide and an RNA atom.
        """
        return cls._bm_bitwise_all_asym_exp(it.PRO_RNA, it.RNA_PRO)

    @hybrid_property
    def is_any_wat(self):
        """
        Returns True if the contact is between a polypeptide and a ligand atom.
        """
        
        return self._bm_bitwise_any(it.WAT_WAT)

    @is_any_wat.expression
    def is_any_wat(cls):
        """
        Returns an SQLAlchemy boolean expression to test if contact is between a
        polypeptide and a ligand atom.
        """
        return cls._bm_bitwise_any_exp(it.WAT_WAT)

    @property
    def sift(self):
        '''
        '''
        return (self.is_clash, self.is_covalent, self.is_vdw_clash, self.is_vdw,
                self.is_proximal, self.is_hbond, self.is_weak_hbond, self.is_xbond,
                self.is_ionic, self.is_metal_complex, self.is_aromatic,
                self.is_hydrophobic, self.is_carbonyl)