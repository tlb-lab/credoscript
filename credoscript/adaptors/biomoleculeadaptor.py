from sqlalchemy.sql.expression import and_

from credoscript.mixins import PathAdaptorMixin
from credoscript.mixins.base import paginate

class BiomoleculeAdaptor(PathAdaptorMixin):
    """
    """
    def __init__(self, paginate=False, per_page=100):
        self.query = Biomolecule.query
        self.paginate = paginate
        self.per_page = per_page

    def fetch_by_biomolecule_id(self, biomolecule_id):
        """
        """
        return self.query.get(biomolecule_id)

    @paginate
    def fetch_all_by_pdb(self, pdb, *expr, **kwargs):
        """
        """
        query = self.query.join('Structure')
        query = query.filter(and_(Structure.pdb==pdb, *expr))

        return query

from ..models.biomolecule import Biomolecule
from ..models.structure import Structure