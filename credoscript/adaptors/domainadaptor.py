from sqlalchemy.sql.expression import and_

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

    @requires.rdkit_catridge
    @paginate
    def fetch_all_by_substruct(self, smiles, *expr, **kwargs):
        """
        Returns all Domains that are in contact with a ligand containing the
        given SMILES substructure.

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

        return query

from ..models.domain import Domain
from ..models.peptide import Peptide
from ..models.chemcomprdmol import ChemCompRDMol
