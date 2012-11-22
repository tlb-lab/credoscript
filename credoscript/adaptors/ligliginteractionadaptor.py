from sqlalchemy.sql.expression import and_

from credoscript.mixins import PathAdaptorMixin
from credoscript.mixins.base import paginate

class LigLigInteractionAdaptor(PathAdaptorMixin):
    """
    Adaptor to fetch ligands from CREDO with different criteria.
    """
    def __init__(self, dynamic=False, paginate=False, per_page=100, options=()):
        """
        """
        self.query = LigLigInteraction.query
        self.dynamic = dynamic
        self.paginate = paginate
        self.per_page = per_page

        # add options to this query: can be joinedload, undefer etc.
        for option in options: self.query = self.query.options(option)

    def fetch_by_lig_lig_interaction_id(self, lig_lig_interaction_id):
        """
        """
        return self.query.get(lig_lig_interaction_id)

    @paginate
    def fetch_all_by_biomolecule_id(self, biomolecule_id, *expr, **kwargs):
        """
        """
        query = self.query.filter(and_(LigLigInteraction.biomolecule_id==biomolecule_id,
                                  *expr))

        return query.distinct()

    @paginate
    def fetch_all_by_ligand_id(self, ligand_id, *expr, **kwargs):
        """
        """
        query = self.query.join('Ligands')
        query = query.filter(and_(Ligand.ligand_id==ligand_id, *expr))

        return query.distinct()

    @paginate
    def fetch_all_by_het_id(self, het_id, *expr, **kwargs):
        """
        """
        query = self.query.join('Ligands')
        query = query.filter(and_(Ligand.ligand_name==het_id.upper(), *expr))

        return query.distinct()

from credoscript.models.ligliginteraction import LigLigInteraction
from credoscript.models.ligand import Ligand