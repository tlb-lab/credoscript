from credoscript import Base, schema

class FragmentHierarchy(Base):
    '''
    '''
    __tablename__ = '%s.fragment_hierarchy' % schema['pdbchem']
    
    def __repr__(self):
        '''
        '''
        return '<FragmentHierarchy({self.fragment_hierarchy_id})>'.format(self=self)
