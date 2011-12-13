from sqlalchemy.sql.expression import and_

from credoscript import session

class ChemCompConformerAdaptor(object):
    '''
    '''
    def __init__(self):
        '''
        '''
        self.query = session.query(ChemCompConformer)

    def fetch_all_by_usr_moments(self, moments, *expressions):
        '''
        '''
        pass

from ..models.chemcompconformer import ChemCompConformer