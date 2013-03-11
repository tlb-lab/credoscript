from sqlalchemy.sql.expression import and_, func

from credoscript.util import requires
from credoscript.mixins.base import paginate

class DomainAdaptor(object):
    """
    """
    def __init__(self, dynamic=False, paginate=False, per_page=100):
        self.query = Domain.query
        self.dynamic = dynamic
        self.paginate = paginate
        self.per_page = per_page

    def fetch_by_domain_id(self, interface_id):
        """
        Parameters
        ----------
        domain_id : int
            Primary key of the `Domain` in CREDO.

        Returns
        -------
        Domain
            CREDO `Domain` object having this groove_id as primary key.

        Examples
        --------
        >>> DomainAdaptor().fetch_by_domain_id(1)
        <Domain(CATH 101mA00)>
        """
        return self.query.get(groove_id)

    @paginate
    def fetch_all_by_chain_id(self, chain_id, *expr, **kwargs):
        """
        """
        query = self.query.join('DomainPeptides','Peptide')
        query = query.filter(and_(Peptide.chain_id==chain_id, *expr))

        return query
    
    @paginate
    def fetch_all_by_fragment_id(self, fragment_id, *expr, **kwargs):
        """
        Returns all protein domains that are in contact with the fragments having
        the given fragment_id.
        
        Parameters
        ----------
        fragment_id : int
            Primary key of the fragment.
        *expr : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried Entities
        ----------------
        Domain, Ligand, LigandFragment

        Returns
        -------
        domains : list
            List of domains that are in contact with the fragments having the
            given fragment_id.
        """
        query = self.query.join('Ligands','LigandFragments')
        query = query.filter(and_(LigandFragment.fragment_id==fragment_id, *expr))

        if kwargs.get('hits'):
            query = query.add_columns(func.count(Ligand.ligand_id.distinct()))
            query = query.group_by(Domain)

        return query.distinct()

    @requires.rdkit_catridge
    @paginate
    def fetch_all_by_substruct(self, smiles, *expr, **kwargs):
        """
        Returns all protein domains that are in contact with a ligand containing
        the given SMILES substructure.

        Parameters
        ----------
        smiles : str
            SMILES string of the substructure to be used for substructure
            searching.
        *expr : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried Entities
        ----------------
        Domain, Ligand, LigandComponent, ChemComp, ChemCompRDMol

        Returns
        -------
        domains : list
            List of domains that are in contact with a ligand containing the
            given SMILES substructure.

        Requires
        --------
        .. important:: `RDKit  <http://www.rdkit.org>`_ PostgreSQL cartridge.
        """
        query = Domain.query.join('Ligands','Components','ChemComp','RDMol')
        query = query.filter(and_(ChemCompRDMol.contains(smiles), *expr))

        if kwargs.get('hits'):
            query = query.add_columns(func.count(Ligand.ligand_id.distinct()))
            query = query.group_by(Domain)

        return query.distinct()

from ..models.domain import Domain
from ..models.ligand import Ligand
from ..models.ligandfragment import LigandFragment
from ..models.peptide import Peptide
from ..models.chemcomprdmol import ChemCompRDMol
