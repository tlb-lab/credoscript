from credoscript import session
from credoscript.mixins import PathAdaptorMixin

class GrooveAdaptor(PathAdaptorMixin):
    '''
    '''
    def __init__(self):
        '''
        '''
        self.query = session.query(Groove)

from ..models.groove import Groove