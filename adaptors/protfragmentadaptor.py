from sqlalchemy.sql.expression import and_

from credoscript.mixins import PathAdaptorMixin

class ProtFragmentAdaptor(PathAdaptorMixin):
    '''
    '''
    def __init__(self):
        self.query = ProtFragment.query
       
    def fetch_by_prot_fragment_id(self, prot_fragment_id):
        '''
        '''
        return self.query.get(prot_fragment_id)

    def fetch_all_by_biomolecule_id(self, biomolecule_id, *expressions):
        '''
        '''
        return self.query.filter(and_(ProtFragment.biomolecule_id==biomolecule_id,
                                      *expressions)).all()

    def fetch_all_by_fragment_seq(self, seq):
        '''
        '''
        return self.query.filter(ProtFragment.fragment_seq==seq).all()

from ..models.protfragment import ProtFragment