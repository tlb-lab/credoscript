from warnings import warn
from credoscript import config

def rdkit(function):
    """
    """
    def wrapper(self, *args, **kwargs):
        """
        """
        if config['extras']['rdkit']:
            return function(self, *args, **kwargs)
        else:
            warn("The RDKit Python wrappers are not installed.", UserWarning)

    return wrapper

def rdkit_catridge(function):
    """
    """
    def wrapper(self, *args, **kwargs):
        """
        """
        if config['extras']['rdkit-cartridge']:
            return function(self, *args, **kwargs)
        else:
            warn("The RDKit PostgreSQL cartridge is not installed on the server.", UserWarning)

    return wrapper
