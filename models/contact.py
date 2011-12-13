from sqlalchemy.orm import relationship

from credoscript import Base

class Contact(Base):
    '''
    Represents a Contact entity from CREDO

    Attributes
    ----------
    contact_id : int
        Primary key.
    '''
    __tablename__ = 'credo.contacts'
    
    AtomBgn  = relationship("Atom",
                            primaryjoin="and_(Atom.atom_id==Contact.atom_bgn_id, Atom.biomolecule_id==Contact.biomolecule_id)", # PARTITION CONSTRAINT-EXCLUSION
                            foreign_keys="[Atom.atom_id, Atom.biomolecule_id]",
                            uselist=False, innerjoin=True)
    
    AtomEnd = relationship("Atom",
                           primaryjoin="and_(Atom.atom_id==Contact.atom_end_id, Atom.biomolecule_id==Contact.biomolecule_id)", # PARTITION CONSTRAINT-EXCLUSION
                           foreign_keys="[Atom.atom_id, Atom.biomolecule_id]",
                           uselist=False, innerjoin=True)    
    
    def __repr__(self):
        '''
        '''
        return "<Contact(%i, %i)>" % (self.atom_bgn_id, self.atom_end_id)

    @property
    def sift(self):
        '''
        '''
        return (self.is_covalent, self.is_vdw_clash, self.is_vdw, self.is_proximal,
                self.is_hbond, self.is_weak_hbond, self.is_xbond, self.is_ionic,
                self.is_metal_complex, self.is_aromatic, self.is_hydrophobic,
                self.is_carbonyl)