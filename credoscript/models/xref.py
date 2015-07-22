from credoscript import Base, schema

class XRef(Base):
    '''
    Represents a cross reference from an external source to an object in CREDO.

    Attributes
    ----------
    xref_id : int
        Primary key.


    Mapped attributes
    -----------------
    Entity : CREDO entity
        CREDO object corresponding to the entity type and identifier of this cross
        reference.

    See Also
    --------


    Notes
    -----
    
    '''
    __tablename__ = '%s.xrefs' % schema['credo']
    
    def __repr__(self):
        '''
        '''
        return '<XRef({self.source} {self.xref})>'.format(self=self)

    @property
    def Entity(self):
        '''
        '''
        if self.entity_type == 'Structure': return StructureAdaptor().fetch_by_structure_id(self.entity_id)
        elif self.entity_type == 'Biomolecule': pass
        elif self.entity_type == 'Chain': return ChainAdaptor().fetch_by_chain_id(self.entity_id)
        elif self.entity_type == 'Ligand': return LigandAdaptor().fetch_by_ligand_id(self.entity_id)
        elif self.entity_type == 'Residue': return ResidueAdaptor().fetch_by_residue_id(self.entity_id)

from ..adaptors.residueadaptor import ResidueAdaptor
from ..adaptors.ligandadaptor import LigandAdaptor
from ..adaptors.chainadaptor import ChainAdaptor
from ..adaptors.structureadaptor import StructureAdaptor