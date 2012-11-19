from sqlalchemy.sql.expression import and_

from credoscript import groove_residues, phenotype_to_groove
from credoscript.mixins import PathAdaptorMixin
from credoscript.mixins.base import paginate

class GrooveAdaptor(PathAdaptorMixin):
    """
    """
    def __init__(self, dynamic=False, paginate=False, per_page=100):
        self.query = Groove.query
        self.dynamic = dynamic
        self.paginate = paginate
        self.per_page = per_page

    def fetch_by_groove_id(self, interface_id):
        """
        Parameters
        ----------
        groove_id : int
            Primary key of the `Groove` in CREDO.

        Returns
        -------
        Groove
            CREDO `Groove` object having this groove_id as primary key.

        Examples
        --------
        >>> GrooveAdaptor().fetch_by_groove_id(1)
        <Groove(1)>
        """
        return self.query.get(groove_id)

    @paginate
    def fetch_all_by_chain_id(self, chain_id, *expr, **kwargs):
        """
        """
        query = self.query.filter(and_(or_(Groove.chain_prot_id==chain_id,
                                           Groove.chain_nuc_id==chain_id),
                                       *expr))

        return query

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

    @paginate
    def fetch_all_by_uniprot(self, uniprot, *expr, **kwargs):
        """
        """
        query = self.query.join('ChainProt','XRefs')
        query = query.filter(and_(XRef.source=='UniProt', XRef.xref==uniprot, *expr))

        return query

    @paginate
    def fetch_all_by_phenotype_id(self, phenotype_id, *expr, **kwargs):
        """
        Returns all grooves whose interacting residues can be linked to
        variations matching the given phenotype_id.
        """
        query = self.query.join(phenotype_to_groove,
                                phenotype_to_groove.c.groove_id==Groove.groove_id)
        query = query.filter(and_(phenotype_to_groove.c.phenotype_id==phenotype_id,
                                  *expr))

        return query

from ..models.groove import Groove
from ..models.peptide import Peptide
from ..models.xref import XRef
