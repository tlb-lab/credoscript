from sqlalchemy.sql.expression import and_

from credoscript.mixins import PathAdaptorMixin

class ProtFragmentAdaptor(PathAdaptorMixin):
    """
    """
    def __init__(self, paginate=False, per_page=100):
        self.paginate = paginate
        self.per_page = per_page
       
    def fetch_by_prot_fragment_id(self, prot_fragment_id):
        """
        """
        return ProtFragment.query.get(prot_fragment_id)

    def fetch_all_by_biomolecule_id(self, biomolecule_id, *expressions):
        """
        """
        return ProtFragment.query.filter(and_(ProtFragment.biomolecule_id==biomolecule_id,
                                              *expressions)).all()

    def fetch_all_by_fragment_seq(self, seq):
        """
        """
        return ProtFragment.query.filter(ProtFragment.fragment_seq==seq).all()
    
    def fetch_all_by_pdb(self, pdb, *expressions, **kwargs):
        """
        """
        query = ProtFragment.query.join('Chain','Biomolecule','Structure')
        query = query.filter(and_(Structure.pdb==pdb.upper(), *expressions))
        
        if self.paginate:
            page = kwargs.get('page',1)
            return query.paginate(page=page, per_page=self.per_page)
            
        else: return query.all()

from ..models.structure import Structure
from ..models.protfragment import ProtFragment