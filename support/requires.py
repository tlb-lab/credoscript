from warnings import warn
from ..meta import HAS_RDKIT, HAS_RDKIT_CARTRIDGE

def rdkit(function):
    '''
    '''
    def wrapper(self, *args, **kwargs):
        '''
        '''
        if HAS_RDKIT:
            return function(self, *args, **kwargs)
        else:
            warn("The RDKit Python wrappers are not installed.", UserWarning)

    return wrapper

def rdkit_catridge(function):
    '''
    '''
    def wrapper(self, *args, **kwargs):
        '''
        '''
        if HAS_RDKIT_CARTRIDGE:
            return function(self, *args, **kwargs)
        else:
            warn("The RDKit PostgreSQL cartridge is not installed on the server.", UserWarning)

    return wrapper