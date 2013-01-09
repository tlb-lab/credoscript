from sqlalchemy.sql.expression import and_

from credoscript.mixins import PathAdaptorMixin
from credoscript.mixins.base import paginate

class LigNucInteractionAdaptor(PathAdaptorMixin):
    """
    Adaptor to fetch ligands from CREDO with different criteria.
    """
    def __init__(self, dynamic=False, paginate=False, per_page=100, options=()):
        """
        """
        self.query = LigNucInteraction.query
        self.dynamic = dynamic
        self.paginate = paginate
        self.per_page = per_page

        # add options to this query: can be joinedload, undefer etc.
        for option in options: self.query = self.query.options(option)

    def fetch_by_lig_nuc_interaction_id(self, lig_nuc_interaction_id):
        """
        """
        return self.query.get(lig_nuc_interaction_id)

    @paginate
    def fetch_all_by_biomolecule_id(self, biomolecule_id, *expr, **kwargs):
        """
        """
        query = self.query.filter(and_(LigNucInteraction.biomolecule_id==biomolecule_id,
                                  *expr))

        return query.distinct()

    @paginate
    def fetch_all_by_ligand_id(self, ligand_id, *expr, **kwargs):
        """
        """
        query = self.query.filter(and_(LigNucInteraction.ligand_id==ligand_id,
                                       *expr))

        return query

    @paginate
    def fetch_all_by_het_id(self, het_id, *expr, **kwargs):
        """
        """
        query = self.query.join('Ligand')
        query = query.filter(and_(Ligand.ligand_name==het_id.upper(), *expr))

        return query.distinct()

    @paginate
    def fetch_all_by_lig_min_hvy_atoms(self, min_hvy_atoms, *expr, **kwargs):
        """
        """
        query = self.query.join('Ligand')
        query = query.filter(and_(Ligand.num_hvy_atoms>=min_hvy_atoms, *expr))

        return query

    @paginate
    def fetch_all_having_drug_like_ligands(self, *expr, **kwargs):
        """
        """
        query = self.query.join('Ligand','ChemComps')
        query = query.filter(and_(ChemComp.is_drug_like==True, *expr))

        return query

    @paginate
    def fetch_all_having_app_drugs(self, *expr, **kwargs):
        """
        """
        query = self.query.join('Ligand','ChemComps')
        query = query.filter(and_(ChemComp.is_approved_drug==True, *expr))

        return query

from credoscript.models.lignucinteraction import LigNucInteraction
from credoscript.models.ligand import Ligand
from credoscript.models.chemcomp import ChemComp