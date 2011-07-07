from sqlalchemy.sql.expression import and_

from ..meta import session

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
        return self.query.join(
            (Residue, Residue.residue_id==Peptide.residue_id)
            ).filter(and_(Residue.chain_id==chain_id, *expressions)).all()

    def fetch_all_by_biomolecule_id(self, biomolecule_id, *expressions):
        '''
        '''
        return self.query.join(
            (Residue, Residue.residue_id==Peptide.residue_id),
            (Chain, Chain.chain_id==Residue.chain_id)
            ).filter(and_(Chain.biomolecule_id==biomolecule_id, *expressions)).all()

from ..models.peptide import Peptide
from ..models.residue import Residue
from ..models.chain import Chain