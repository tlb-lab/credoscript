from sqlalchemy.sql.expression import and_

from credoscript.mixins.base import paginate

class DomainAdaptor(object):
    """
    """
    def __init__(self, dynamic=False, paginate=False, per_page=100):
        self.query = Domain.query
        self.dynamic = dynamic
        self.paginate = paginate
        self.per_page = per_page

    def fetch_by_domain_id(self, interface_id):
        """
        Parameters
        ----------
        domain_id : int
            Primary key of the `Domain` in CREDO.

        Returns
        -------
        Domain
            CREDO `Domain` object having this groove_id as primary key.

        Examples
        --------
        >>> DomainAdaptor().fetch_by_domain_id(1)
        <Domain(CATH 101mA00)>
        """
        return self.query.get(groove_id)

    @paginate
    def fetch_all_by_chain_id(self, chain_id, *expr, **kwargs):
        """
        """
        query = self.query.join('DomainPeptides','Peptide')
        query = query.filter(and_(Peptide.chain_id==chain_id, *expr))

        return query

from ..models.domain import Domain
from ..models.peptide import Peptide
