from .model import Model

class XRef(Model):
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
    def __repr__(self):
        '''
        '''
        return '<XRef({self.source} {self.xref})>'.format(self=self)

    def __getitem__(self, pdb_chain_id):
        '''
        '''
        return self.Chains[pdb_chain_id]

    def __hash__(self):
        '''
        '''
        return self.xref_id

    def __eq__(self, other):
        '''
        '''
        return self.xref_id == other.xref_id

    def __ne__(self, other):
        '''
        '''
        return self.xref_id != other.xref_id

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