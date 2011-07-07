from .model import Model

class Peptide(Model):
    '''
    '''
    def __repr__(self):
        '''
        '''
        return '<Peptide({self.residue_id})>'.format(self=self)

    def __getitem__(self):
        '''
        '''
        pass

    def __iter__(self):
        '''
        '''
        return self.Atoms