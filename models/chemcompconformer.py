from credoscript import Base

class ChemCompConformer(Base):
    '''
    '''
    __tablename__ = 'pdbchem.chem_comp_conformers'
    
    def __repr__(self):
        '''
        '''
        return '<ChemCompConformer({self.het_id} {self.conformer})>'.format(self=self)

    def usrcat(self):
        '''
        '''
        pass