from sqlalchemy.sql.expression import and_

from credoscript.mixins import PathAdaptorMixin

class ChainAdaptor(PathAdaptorMixin):
    """
    """
    def __init__(self, paginate=False, per_page=100):
        """
        """
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
        return Chain.query.get(chain_id)

    def fetch_all_by_structure_id(self, structure_id, *expressions):
        """
        """
        query = Chain.query.join('Biomolecule').filter(
            and_(Biomolecule.structure_id==structure_id, *expressions))

        return query.all()

    def fetch_all_by_uniprot(self, uniprot, **kwargs):
        """
        """
        query = Chain.query.join('XRefs')
        query = query.filter(and_(XRef.source=='UniProt', XRef.xref==uniprot))

        if self.paginate:
            page = kwargs.get('page',1)
            return query.paginate(page=page, per_page=self.per_page)
            
        else: return query.all()

    def fetch_all_by_cath_dmn(self, dmn):
        """
        """
        query = Chain.query.join('XRefs').filter(
            and_(XRef.entity_type=='Chain', XRef.entity_id==Chain.chain_id,
                 XRef.source=='CATH', XRef.xref==dmn))

        return query.all()

    def fetch_all_by_seq_md5(self, md5, *expressions):
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
        return Chain.query.filter(Chain.chain_seq_md5==md5).all()

from ..models.xref import XRef
from ..models.chain import Chain
from ..models.biomolecule import Biomolecule