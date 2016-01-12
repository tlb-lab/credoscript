from sqlalchemy.orm import relationship

from credoscript import Base, schema

class LigandFragmentAtom(Base):
    '''
    '''
    __tablename__ = '%s.ligand_fragment_atoms' % schema['credo']
    
    Atom  = relationship("Atom",
                         primaryjoin="Atom.atom_id==LigandFragmentAtom.atom_id",
                         foreign_keys="[Atom.atom_id]",
                         uselist=False)