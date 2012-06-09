from sqlalchemy.orm import backref, relationship

from credoscript import Base

class Fragment(Base):
    """
    Class representing a Fragment entity from CREDO.

    Attributes
    ----------
    fragment_id
    ism

    Mapped Attributes
    -----------------
    ChemCompFragments : Query
    ChemComps : Query
        Chemical components that share this fragment.
    """
    __tablename__ = 'pdbchem.fragments'

    ChemCompFragments = relationship("ChemCompFragment",
                                       primaryjoin="ChemCompFragment.fragment_id==Fragment.fragment_id",
                                       foreign_keys = "[ChemCompFragment.fragment_id]",
                                       lazy='dynamic', uselist=True, innerjoin=True,
                                       backref=backref('Fragment', uselist=False,
                                                       remote_side="[ChemCompFragment.fragment_id]"))

    ChemComps = relationship("ChemComp",
                              secondary=Base.metadata.tables['pdbchem.chem_comp_fragments'],
                              primaryjoin="Fragment.fragment_id==ChemCompFragment.fragment_id",
                              secondaryjoin="ChemCompFragment.het_id==ChemComp.het_id",
                              foreign_keys="[ChemCompFragment.fragment_id, ChemComp.het_id]",
                              lazy='dynamic', uselist=True, innerjoin=True)

    def __repr__(self):
        """
        """
        return '<Fragment({self.fragment_id})>'.format(self=self)

    @property
    def Children(self):
        """
        Returns all fragments that are derived from this fragment (next level
        in fragmentation hierarchy).
        """
        return FragmentAdaptor().fetch_all_children(self.fragment_id, dynamic=True)

    @property
    def Parents(self):
        """
        """
        return FragmentAdaptor().fetch_all_parents(self.fragment_id, dynamic=True)

    @property
    def Leaves(self):
        """
        Returns all terminal fragments (leaves) of this fragment.
        """
        return FragmentAdaptor().fetch_all_leaves(self.fragment_id, dynamic=True)

    @property
    def Descendants(self):
        """
        Returns all children of this fragment in the complete hierarchy.
        """
        return FragmentAdaptor().fetch_all_descendants(self.fragment_id, dynamic=True)

from ..adaptors.fragmentadaptor import FragmentAdaptor
