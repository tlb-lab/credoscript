from sqlalchemy.orm import backref, relationship

from credoscript import Base
from credoscript.mixins import PathMixin

class ProtFragment(Base, PathMixin):
    '''
    '''
    __tablename__ = 'credo.prot_fragments'

    Peptides = relationship("Peptide",
                            secondary = Base.metadata.tables['credo.prot_fragment_residues'],
                            primaryjoin = "ProtFragment.prot_fragment_id==ProtFragmentResidue.prot_fragment_id",
                            secondaryjoin = "ProtFragmentResidue.residue_id==Peptide.residue_id",
                            foreign_keys = "[ProtFragmentResidue.prot_fragment_id, Peptide.residue_id]",
                            uselist=True, innerjoin=True, lazy='dynamic',
                            backref = backref('ProtFragment', uselist=False, innerjoin=True))

    def __repr__(self):
        '''
        '''
        return '<ProtFragment({self.path})>'.format(self=self)

    @property
    def ProtFragmentN(self):
        '''
        '''
        return ProtFragmentAdaptor().fetch_by_prot_fragment_id(self.prot_fragment_nterm_id)

    @property
    def ProtFragmentC(self):
        '''
        '''
        return ProtFragmentAdaptor().fetch_by_prot_fragment_id(self.prot_fragment_cterm_id)

    @property
    def IdenticalFragments(self):
        '''
        '''
        return ProtFragmentAdaptor().fetch_all_by_fragment_seq(self.fragment_seq, dynamic=True)

from ..adaptors.protfragmentadaptor import ProtFragmentAdaptor
