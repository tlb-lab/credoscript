from credoscript import Base

class FragmentHierarchy(Base):
    '''
    '''
    __tablename__ = 'pdbchem.fragments'
    
    def __repr__(self):
        '''
        '''
        return '<FragmentHierarchy({self.fragment_hierarchy_id})>'.format(self=self)
