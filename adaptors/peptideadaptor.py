from sqlalchemy.sql.expression import and_

from credoscript import session
from credoscript.mixins import PathAdaptorMixin, ResidueAdaptorMixin

class PeptideAdaptor(ResidueAdaptorMixin, PathAdaptorMixin):
    '''
    '''
    def __init__(self):
        '''
        '''
        self.query = session.query(Peptide)

from ..models.peptide import Peptide