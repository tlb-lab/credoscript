from sqlalchemy.sql.expression import and_

from credoscript import phenotype_to_chain
from credoscript.mixins import PathAdaptorMixin
from credoscript.mixins.base import paginate

class ChainAdaptor(PathAdaptorMixin):
    """
    """
    def __init__(self, dynamic=False, paginate=False, per_page=100):
        self.query = Chain.query
        self.dynamic = dynamic
        self.paginate = paginate
        self.per_page = per_page

    def fetch_by_chain_id(self, chain_id):
        """
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
        """
        return self.query.get(chain_id)

    @paginate
    def fetch_all_by_structure_id(self, structure_id, *expr, **kwargs):
        """
        """
        query = self.query.join('Biomolecule')
        query = query.filter(and_(Biomolecule.structure_id==structure_id, *expr))

        return query

    @paginate
    def fetch_all_polypeptides(self, *expr, **kwargs):
        """
        """
        query = self.query.join('Polypeptide')
        query = query.filter(and_(*expr))

        return query

    @paginate
    def fetch_all_kinases(self, *expr, **kwargs):
        """
        """
        query = self.query.join('Polypeptide')
        query = query.filter(and_(Polypeptide.is_kinase==True, *expr))

        return query

    @paginate
    def fetch_all_biotherapeutics(self, *expr, **kwargs):
        """
        """
        query = self.query.join('XRefs')
        query = query.filter(and_(XRef.source=='ChEMBL Biotherapeutic', *expr))

        return query.distinct()

    @paginate
    def fetch_all_oligonucleotides(self, *expr, **kwargs):
        """
        """
        query = self.query.join('Oligonucleotide')
        query = query.filter(and_(*expr))

        return query

    @paginate
    def fetch_all_by_uniprot(self, uniprot, *expr, **kwargs):
        """
        """
        query = self.query.join('XRefs')
        query = query.filter(and_(XRef.source=='UniProt',
                                  XRef.xref==uniprot, *expr))

        return query.distinct()

    @paginate
    def fetch_all_by_cath_dmn(self, dmn, *expr, **kwargs):
        """
        """
        query = self.query.join('XRefs')
        query = query.filter(and_(XRef.entity_type=='Chain',
                                  XRef.entity_id==Chain.chain_id,
                                  XRef.source=='CATH', XRef.xref==dmn, *expr))

        return query

    @paginate
    def fetch_all_by_go(self, go, *expr, **kwargs):
        """
        """
        query = self.query.join('XRefs')
        query = query.filter(and_(XRef.source=='GO',
                                  XRef.xref==go, *expr))

        return query.distinct()

    @paginate
    def fetch_all_by_seq_md5(self, md5, *expr, **kwargs):
        """
        Returns all chains in CREDO whose protein sequences MD5 hash match the
        specified MD5 hash (of another protein sequence).

        Parameters
        ----------
        md5 : str
            MD5 hash of a protein sequence.
        *expressions : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Returns
        -------
        Chains : list
            Chains in CREDO whose protein sequences MD5 hash match the specified
            MD5 hash.

        Examples
        --------
        ChainAdaptor().fetch_all_by_seq_md5('02F49E94352EADF3DE9DC9416502ED7F')
        [<Chain(A)>, <Chain(A)>, <Chain(A)>, <Chain(A)>, <Chain(A)>, ...]
        """
        query = self.query.filter(and_(Chain.seq_md5==md5, *expr))

        return query

    @paginate
    def fetch_all_by_phenotype_id(self, phenotype_id, *expr, **kwargs):
        """
        Returns all chains that contain residues that are linked to variations
        matching the given phenotype_id (from EnsEMBL).
        """
        query = self.query.join(phenotype_to_chain,
                                phenotype_to_chain.c.chain_id==Chain.chain_id)
        query = query.filter(and_(phenotype_to_chain.c.phenotype_id==phenotype_id,
                                  *expr))

        return query.distinct()

from ..models.xref import XRef
from ..models.chain import Chain, Polypeptide
from ..models.biomolecule import Biomolecule