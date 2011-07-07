from sqlalchemy.sql.expression import and_

from ..meta import session

class ChainAdaptor(object):
    '''
    '''
    def __init__(self):
        '''
        '''
        self.query = session.query(Chain)

    def fetch_by_chain_id(self, chain_id):
        '''
        Returns the Chain with the given CREDO chain_id.

        Parameters
        ----------
        chain_id : int
            Primary key of the Chain in CREDO.

        Returns
        -------
        Chain
            CREDO Chain object having this chain_id as primary key.

        Examples
        --------
        >>> ChainAdaptor().fetch_by_chain_id(318)
        >>> <Chain(F)>
        '''
        return self.query.get(chain_id)

    def fetch_all_by_structure_id(self, structure_id, *expressions):
        '''
        '''
        query = self.query.join('Biomolecule').filter(
            and_(Biomolecule.structure_id==structure_id, *expressions))

        return query.all()

    def fetch_all_by_uniprot(self, uniprot):
        '''
        '''
        query = self.query.join('XRefs').filter(
            and_(XRef.entity_type=='Chain', XRef.entity_id==Chain.chain_id,
                 XRef.source=='UniProt', XRef.xref==uniprot))

        return query.all()

    def fetch_all_by_cath_dmn(self, dmn):
        '''
        '''
        query = self.query.join('XRefs').filter(
            and_(XRef.entity_type=='Chain', XRef.entity_id==Chain.chain_id,
                 XRef.source=='CATH', XRef.xref==dmn))

        return query.all()

from ..models.xref import XRef
from ..models.chain import Chain
from ..models.biomolecule import Biomolecule