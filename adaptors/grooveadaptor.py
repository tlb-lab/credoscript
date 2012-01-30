from credoscript.mixins import PathAdaptorMixin

class GrooveAdaptor(PathAdaptorMixin):
    '''
    '''
    def __init__(self):
        self.query = Groove.query

from ..models.groove import Groove