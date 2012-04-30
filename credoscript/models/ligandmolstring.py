from credoscript import Base

class LigandMolString(Base):
    '''
    '''
    __tablename__ = 'credo.ligand_molstrings'    
    
    def __repr__(self):
        '''
        '''
        return '<LigandMolString({self.ligand_id})>'.format(self=self)