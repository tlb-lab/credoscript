from .model import Model

class ProtFragment(Model):
    '''
    '''
    def __repr__(self):
        '''
        '''
        return '<ProtFragment({self.sstruct} {self.fragment_size})>'.format(self=self)

    def __iter__(self):
        '''
        '''
        pass

from ..adaptors.residueadaptor import ResidueAdaptor