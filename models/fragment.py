from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql.expression import and_, func

from credoscript import Base

class Fragment(Base):
    '''
    '''
    __tablename__ = 'pdbchem.chem_comp_fragments'
    
    ChemCompFragments = relationship("ChemCompFragment",
                                     primaryjoin="ChemCompFragment.fragment_id==Fragment.fragment_id",
                                     foreign_keys = "[ChemCompFragment.fragment_id]",
                                     uselist=True, innerjoin=True,
                                     backref=backref('Fragment', uselist=False,
                                                     remote_side="[ChemCompFragment.fragment_id]"))
    
    def __repr__(self):
        '''
        '''
        return '<Fragment({self.fragment_id})>'.format(self=self)

    @property
    def Children(self):
        '''
        Returns all fragments that are derived from this fragment (next level
        in fragmentation hierarchy).
        '''
        return FragmentAdaptor().fetch_all_children(self.fragment_id)

    @property
    def Parents(self):
        '''
        '''
        return FragmentAdaptor().fetch_all_parents(self.fragment_id)

    @property
    def Leaves(self):
        '''
        Returns all terminal fragments (leaves) of this fragment.
        '''
        return FragmentAdaptor().fetch_all_leaves(self.fragment_id)

    @property
    def Descendants(self):
        '''
        Returns all children of this fragment in the complete hierarchy.
        '''
        return FragmentAdaptor().fetch_all_descendants(self.fragment_id)

    def get_chem_comps(self, *expressions):
        '''
        '''
        return ChemCompAdaptor().fetch_all_by_fragment_id(self.fragment_id, *expressions)

from .fragmenthierarchy import FragmentHierarchy
from ..adaptors.chemcompadaptor import ChemCompAdaptor
from ..adaptors.fragmentadaptor import FragmentAdaptor