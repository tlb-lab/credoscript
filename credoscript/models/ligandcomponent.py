from sqlalchemy.orm import backref, relationship

from credoscript import Base

class LigandComponent(Base):
    """
    Represents a PDB residue that is part of a ligand in CREDO.

    Overloaded operators
    --------------------
    """
    __tablename__ = 'credo.ligand_components'

    Atoms = relationship("Atom",
                         primaryjoin = "Atom.residue_id==LigandComponent.residue_id",
                         foreign_keys = "[Atom.residue_id]",
                         innerjoin=True, uselist=True, lazy='dynamic')

    Residue = relationship("Residue",
                           primaryjoin="Residue.residue_id==LigandComponent.residue_id",
                           foreign_keys="[Residue.residue_id]", uselist=False, innerjoin=True)

    ChemComp = relationship("ChemComp",
                            primaryjoin = "LigandComponent.het_id==ChemComp.het_id",
                            foreign_keys = "[ChemComp.het_id]",
                            uselist=False, innerjoin=True,
                            backref=backref('LigandComponents', uselist=True, innerjoin=True))

    LigandFragments = relationship("LigandFragment",
                                   primaryjoin = "LigandFragment.ligand_component_id==LigandComponent.ligand_component_id",
                                   foreign_keys = "[LigandFragment.ligand_component_id]",
                                   uselist=True, innerjoin=True, lazy='dynamic',
                                   backref=backref('LigandComponent', uselist=False, innerjoin=True))

    def __repr__(self):
        '''
        '''
        return '<LigandComponent({self.ligand_id} {self.residue_id})>'.format(self=self)
