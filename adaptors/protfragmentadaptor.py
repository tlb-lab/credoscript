from sqlalchemy.sql.expression import and_

from ..meta import session

class ProtFragmentAdaptor(object):
    '''
    '''
    def __init__(self):
        '''
        '''
        self.query = session.query(ProtFragment)

    def fetch_by_prot_fragment_id(self, prot_fragment_id):
        '''
        '''
        return self.query.get(prot_fragment_id)

    def fetch_all_by_biomolecule_id(self, biomolecule_id, *expressions):
        '''
        '''
        return self.query.filter(and_(ProtFragment.biomolecule_id==biomolecule_id,
                                      *expressions)).all()

from ..models.protfragment import ProtFragment