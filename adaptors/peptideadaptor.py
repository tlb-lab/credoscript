from sqlalchemy.sql.expression import and_

from credoscript.mixins import PathAdaptorMixin, ResidueAdaptorMixin

class PeptideAdaptor(ResidueAdaptorMixin, PathAdaptorMixin):
    """
    """
    def fetch_by_res_map_id(self, res_map_id):
        """
        """
        return Peptide.query.filter_by(res_map_id=res_map_id).first()
       
from ..models.peptide import Peptide