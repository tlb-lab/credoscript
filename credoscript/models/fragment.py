from sqlalchemy.orm import backref, relationship, column_property
from sqlalchemy import select

from credoscript import Base, BaseQuery, schema

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
    __tablename__ = '%s.fragments' % schema['pdbchem']

    ChemCompFragments = relationship("ChemCompFragment",
                                       primaryjoin="ChemCompFragment.fragment_id==Fragment.fragment_id",
                                       foreign_keys = "[ChemCompFragment.fragment_id]",
                                       lazy='dynamic', uselist=True, innerjoin=True,
                                       backref=backref('Fragment', uselist=False, innerjoin=True, lazy=False))

    ChemComps = relationship("ChemComp", query_class=BaseQuery,
                              secondary=Base.metadata.tables['%s.chem_comp_fragments' % schema['pdbchem']],
                              primaryjoin="Fragment.fragment_id==ChemCompFragment.fragment_id",
                              secondaryjoin="ChemCompFragment.het_id==ChemComp.het_id",
                              foreign_keys="[ChemCompFragment.fragment_id, ChemComp.het_id]",
                              lazy='dynamic', uselist=True, innerjoin=True) # 
                              
    RDMol = relationship("FragmentRDMol",
                         primaryjoin="FragmentRDMol.fragment_id==Fragment.fragment_id",
                         foreign_keys="[FragmentRDMol.fragment_id]",
                         uselist=False, innerjoin=True,
                         backref=backref('Fragment', uselist=False, innerjoin=True))

    RDFP = relationship("FragmentRDFP",
                        primaryjoin="FragmentRDFP.fragment_id==Fragment.fragment_id",
                        foreign_keys="[FragmentRDFP.fragment_id]",
                        uselist=False, innerjoin=True,
                        backref=backref('Fragment', uselist=False, innerjoin=True))

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
        adaptor = FragmentAdaptor(dynamic=True)
        return adaptor.fetch_all_children(self.fragment_id)

    @property
    def Parents(self):
        """
        """
        adaptor = FragmentAdaptor(dynamic=True)
        return adaptor.fetch_all_parents(self.fragment_id)

    @property
    def Leaves(self):
        """
        Returns all terminal fragments (leaves) of this fragment.
        """
        adaptor = FragmentAdaptor(dynamic=True)
        return adaptor.fetch_all_leaves(self.fragment_id)

    @property
    def Descendants(self):
        """
        Returns all children of this fragment in the complete hierarchy.
        """
        adaptor = FragmentAdaptor(dynamic=True)
        return adaptor.fetch_all_descendants(self.fragment_id)
        
    @classmethod
    def like(self, smiles):
        """
        Returns an SQL function expression that uses the PostgreSQL trigram index
        to compare the SMILES strings.
        """
        return self.ism.op('%%')(smiles)

from ..adaptors.fragmentadaptor import FragmentAdaptor

