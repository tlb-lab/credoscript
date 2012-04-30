from sqlalchemy.sql.expression import and_

class ChemCompConformerAdaptor(object):
    '''
    '''
    def __init__(self):
        self.query = ChemCompConformer.query
       
    def fetch_all_by_usr_moments(self, moments, *expressions):
        '''
        '''
        pass

from ..models.chemcompconformer import ChemCompConformer