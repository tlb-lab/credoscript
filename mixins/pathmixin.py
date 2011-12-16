from sqlalchemy.orm import deferred

class PathMixin(object):
    '''
    This Mixin is used to add methods for the ptree path attribute of some CREDO
    entities. 
    '''
    @classmethod
    def pquery(self, query):
        '''
        Returns "ptree matches pquery" as SQL expression.
        '''
        return self.path.op('~')(query)
    
    @classmethod
    def pancestor(self, ptree):
        '''
        Returns "is left argument an ancestor of right (or equal)?" as SQL expression.
        '''
        return self.path.op('@>')(ptree)