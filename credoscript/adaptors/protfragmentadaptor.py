from sqlalchemy.sql.expression import and_

from credoscript import binding_sites, prot_fragment_residues
from credoscript.mixins import PathAdaptorMixin
from credoscript.mixins.base import paginate

class ProtFragmentAdaptor(PathAdaptorMixin):
    """
    """
    def __init__(self, paginate=False, per_page=100):
        self.query = ProtFragment.query
        self.paginate = paginate
        self.per_page = per_page

    def fetch_by_prot_fragment_id(self, prot_fragment_id):
        """
        """
        return self.query.get(prot_fragment_id)

    @paginate
    def fetch_all_by_biomolecule_id(self, biomolecule_id, *expr, **kwargs):
        """
        """
        query = self.query.join('Chain')
        query = query.filter(and_(Chain.biomolecule_id==biomolecule_id, *expr))

        return query

    @paginate
    def fetch_all_by_fragment_seq(self, seq, *expr, **kwargs):
        """
        """
        query = self.query.filter(ProtFragment.fragment_seq==seq)
        query = query.filter(and_(*expr))

        return query

    @paginate
    def fetch_all_by_pdb(self, pdb, *expr, **kwargs):
        """
        """
        query = self.query.join('Chain','Biomolecule','Structure')
        query = query.filter(and_(Structure.pdb==pdb.upper(), *expr))

        return query

    @paginate
    def fetch_all_in_contact_with_ligand_id(self, ligand_id, *expr,
                                            **kwargs):
        """
        """
        query = self.query
        query = query.join(prot_fragment_residues,
                           prot_fragment_residues.c.prot_fragment_id==ProtFragment.prot_fragment_id)
        query = query.join(binding_sites,
                           binding_sites.c.residue_id==prot_fragment_residues.c.residue_id)
        query = query.filter(and_(binding_sites.c.ligand_id==ligand_id, *expr))

        return query.distinct()

from ..models.structure import Structure
from ..models.chain import Chain
from ..models.protfragment import ProtFragment