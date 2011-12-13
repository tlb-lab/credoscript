from sqlalchemy.sql.expression import and_

from credoscript import session

class PeptideAdaptor(object):
    '''
    '''
    def __init__(self):
        '''
        '''
        self.query = session.query(Peptide)

    def fetch_by_residue_id(self, residue_id):
        '''
        '''
        return self.query.get(residue_id)

    def fetch_all_by_chain_id(self, chain_id, *expressions):
        '''
        '''
        return self.query.filter(and_(Peptide.chain_id==chain_id, *expressions)).all()

    def fetch_all_by_biomolecule_id(self, biomolecule_id, *expressions):
        '''
        '''
        return self.query.filter(and_(Peptide.biomolecule_id==biomolecule_id, *expressions)).all()

from ..models.peptide import Peptide