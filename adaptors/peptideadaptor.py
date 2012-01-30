from sqlalchemy.sql.expression import and_

from credoscript.mixins import PathAdaptorMixin, ResidueAdaptorMixin

class PeptideAdaptor(ResidueAdaptorMixin, PathAdaptorMixin):
    '''
    '''
    def __init__(self):
        self.query = Peptide.query
       
from ..models.peptide import Peptide