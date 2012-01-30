from sqlalchemy.sql.expression import and_

from credoscript.mixins import PathAdaptorMixin

class BiomoleculeAdaptor(PathAdaptorMixin):
    '''
    '''
    def __init__(self):
        self.query = Biomolecule.query
    
    def fetch_by_biomolecule_id(self, biomolecule_id):
        '''
        '''
        return self.query.get(biomolecule_id)

    def fetch_all_by_pdb(self, pdb):
        '''
        '''
        return self.query.join('Structure').filter(Structure.pdb==pdb).all()

from ..models.biomolecule import Biomolecule
from ..models.structure import Structure