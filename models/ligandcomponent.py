from sqlalchemy.orm import backref, relationship
from sqlalchemy.orm.collections import attribute_mapped_collection

from credoscript import Base

class LigandComponent(Base):
    '''
    Represents a PDB residue that is part of a ligand in CREDO.

    Overloaded operators
    --------------------
    __getitem__(self, other)
        If the other item is a fragment, all the fragment atoms in this component
        are returned through the get_fragment_atoms() method of this class.
    '''
    __tablename__ = 'credo.ligand_components'
    
    Atoms = relationship("Atom",
                         collection_class=attribute_mapped_collection("atom_name"),
                         primaryjoin = "Atom.residue_id==LigandComponent.residue_id",
                         foreign_keys = "[Atom.residue_id]", innerjoin=True, uselist=True)
    
    Residue = relationship("Residue",
                           primaryjoin="Residue.residue_id==LigandComponent.residue_id",
                           foreign_keys="[Residue.residue_id]", uselist=False, innerjoin=True)
        
    ChemComp = relationship("ChemComp",
                            secondary = Base.metadata.tables['credo.residues'],
                            primaryjoin = "LigandComponent.residue_id==Residue.residue_id",
                            secondaryjoin = "Residue.res_name==ChemComp.het_id",
                            foreign_keys = "[Residue.residue_id,Residue.res_name]",
                            uselist=False, innerjoin=True,
                            backref=backref('LigandComponents', uselist=True, innerjoin=True))
        
    LigandFragments = relationship("LigandFragment",
                                   primaryjoin = "LigandFragment.ligand_component_id==LigandComponent.ligand_component_id",
                                   foreign_keys = "[LigandFragment.ligand_component_id]",
                                   uselist=True, innerjoin=True,
                                   backref=backref('LigandComponent', uselist=False, innerjoin=True))    
    
    def __repr__(self):
        '''
        '''
        return '<LigandComponent({self.ligand_id} {self.residue_id})>'.format(self=self)

    def __getitem__(self, other):
        '''
        '''
        if isinstance(other, str): return self.Atoms.get(other)