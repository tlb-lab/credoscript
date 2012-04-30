from sqlalchemy.sql.expression import and_

from credoscript.mixins import PathAdaptorMixin, ResidueAdaptorMixin
from credoscript.mixins.base import paginate

class PeptideAdaptor(ResidueAdaptorMixin, PathAdaptorMixin):
    """
    """
    def __init__(self, paginate=False, per_page=100):
        self.query = Peptide.query
        self.paginate = paginate
        self.per_page = per_page

    def fetch_by_res_map_id(self, res_map_id):
        """
        """
        return self.query.filter_by(res_map_id=res_map_id).first()

    @paginate
    def fetch_all_by_variation_id(self, variation_id, *expr, **kwargs):
        """
        """
        query = self.query.join('Variation2PDB','Variation2UniProt')
        query = query.filter(and_(Variation2UniProt.variation_id==variation_id,
                                  *expr))

        # add more variation data to the returned entities
        if kwargs.get('vardata'):
            query = query.add_columns(Variation2UniProt.mut,
                                      Variation2UniProt.polyphen_prediction,
                                      Variation2UniProt.sift_prediction)

        return query.distinct()

    @paginate
    def fetch_all_by_phenotype_id(self, phenotype_id, *expr, **kwargs):
        """
        """
        query = self.query.join('Variation2PDB','Variation2UniProt','Variation','Annotations')
        query = query.filter(and_(Annotation.phenotype_id==phenotype_id,
                                  *expr))

        return query.distinct()

from ..models.peptide import Peptide
from ..models.variation import Variation2UniProt, Annotation