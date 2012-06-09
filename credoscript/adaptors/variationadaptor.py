from sqlalchemy.sql.expression import and_

from credoscript.mixins.base import paginate

class VariationAdaptor(object):
    """
    """
    def __init__(self, paginate=False, per_page=100):
        self.query = Variation.query
        self.paginate = paginate
        self.per_page = per_page

    def fetch_by_variation_id(self, variation_id):
        """
        """
        return self.query.get(variation_id)

    @paginate
    def fetch_all_by_res_map_id(self, res_map_id, *expr, **kwargs):
        """
        """
        query = self.query.join('Variation2PDB')
        query = query.filter(Variation2PDB.res_map_id==res_map_id)

        return query

    @paginate
    def fetch_all_by_chain_id(self, chain_id, *expr, **kwargs):
        """
        """
        query = self.query.join('Variation2PDB')
        query = query.join(Peptide, Peptide.res_map_id==Variation2PDB.res_map_id)
        query = query.filter(and_(Peptide.chain_id==chain_id, *expr))

        return query

    @paginate
    def fetch_all_ext_by_chain_id(self, chain_id, *expr, **kwargs):
        """
        """
        query = self.query.join('Variation2UniProt','Variation2PDB','Peptide')
        query = query.filter(and_(Peptide.chain_id==chain_id, *expr))

        query = query.add_entity(Variation2UniProt)
        query = query.add_entity(Peptide)

        return query

    @paginate
    def fetch_all_by_phenotype_id(self, phenotype_id, *expr, **kwargs):
        """
        """
        query = self.query.join('Annotations')
        query = query.filter(and_(Annotation.phenotype_id==phenotype_id, *expr))
        query = query.distinct()

        return query

from ..models.variation import Variation, Annotation, Variation2UniProt, Variation2PDB
from ..models.peptide import Peptide
