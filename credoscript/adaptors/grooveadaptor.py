from credoscript.mixins import PathAdaptorMixin
from credoscript.mixins.base import paginate

class GrooveAdaptor(PathAdaptorMixin):
    """
    """
    def __init__(self, paginate=False, per_page=100):
        self.query = Groove.query
        self.paginate = paginate
        self.per_page = per_page

    @paginate
    def fetch_all_by_uniprot(self, uniprot, *expr, **kwargs):
        """
        """
        query = self.query.join('ChainProt','XRefs')
        query = query.filter(and_(XRef.source=='UniProt', XRef.xref==uniprot, *expr))

        return query

    @paginate
    def fetch_all_by_cath_dmn(self, dmn, *expr, **kwargs):
        """
        """
        query = self.query.join(groove_residues, groove_residues.c.groove_id==Groove.groove_id)
        query = query.join(Peptide, Peptide.residue_id==groove_residues.c.residue_prot_id)
        query = query.filter(and_(Peptide.cath==dmn, *expr))

        return query

from ..models.groove import Groove
from ..models.xref import XRef