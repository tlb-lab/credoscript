from .model import Model
from ..meta import session

class LigandComponent(Model):
    '''
    Represents a PDB residue that is part of a ligand in CREDO.

    Overloaded operators
    --------------------
    __getitem__(self, other)
        If the other item is a fragment, all the fragment atoms in this component
        are returned through the get_fragment_atoms() method of this class.
    '''
    def __repr__(self):
        '''
        '''
        return '<LigandComponent({self.ligand_id} {self.residue_id})>'.format(self=self)

    def __getitem__(self, other):
        '''
        '''
        if isinstance(other, str): return self.Atoms.get(other)

    def __hash__(self):
        '''
        '''
        return self.ligand_id

    def __eq__(self, other):
        '''
        '''
        return self.ligand_id == other.ligand_id

    def __ne__(self, other):
        '''
        '''
        return self.ligand_id != other.ligand_id

from .fragment import Fragment
from .atom import Atom
from .residue import Residue
from ..adaptors.chemcompadaptor import ChemCompAdaptor