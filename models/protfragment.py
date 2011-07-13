from .model import Model

class ProtFragment(Model):
    '''
    '''
    def __repr__(self):
        '''
        '''
        return '<ProtFragment({self.sstruct} {self.fragment_size})>'.format(self=self)

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
        return ProtFragmentAdaptor().fetch_all_by_fragment_seq(self.fragment_seq)

from ..adaptors.protfragmentadaptor import ProtFragmentAdaptor