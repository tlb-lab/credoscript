from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql.expression import and_, func

from credoscript import Base

class Fragment(Base):
    '''
    '''
    __tablename__ = 'pdbchem.fragments'
    
    ChemCompFragments = relationship("ChemCompFragment",
                                     primaryjoin="ChemCompFragment.fragment_id==Fragment.fragment_id",
                                     foreign_keys = "[ChemCompFragment.fragment_id]",
                                     uselist=True, innerjoin=True,
                                     backref=backref('Fragment', uselist=False,
                                                     remote_side="[ChemCompFragment.fragment_id]"))
    
    # MANY-TO-MANY RELATIONSHIP
    ChemComps = relationship("ChemComp",
                             secondary=Base.metadata.tables['pdbchem.chem_comp_fragments'],
                             primaryjoin="Fragment.fragment_id==ChemCompFragment.fragment_id",
                             secondaryjoin="ChemCompFragment.het_id==ChemComp.het_id",
                             foreign_keys="[ChemCompFragment.fragment_id, ChemComp.het_id]",
                             uselist=True, innerjoin=True)       
    
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

from .fragmenthierarchy import FragmentHierarchy
from ..adaptors.fragmentadaptor import FragmentAdaptor