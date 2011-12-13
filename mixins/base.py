from collections import OrderedDict
from sqlalchemy.orm import class_mapper

class ClassProperty(property):
    '''
    Analogous to the property() function but for class methods.
    From http://stackoverflow.com/questions/128573/using-property-on-classmethods
    '''
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()

class Base(object):
    '''
    '''
    __table_args__ = {'autoload':True}
    
    @ClassProperty
    @classmethod
    def __meta__(cls):
        '''
        Returns the metadata information of this class as ordered dictionary.
        '''
        mapper = class_mapper(cls)
        
        return OrderedDict([(str(key), str(mapper.c[key].type)) for key in mapper.c.keys()])
    
    @property 
    def __data__(self):
        '''
        Returns a list of values for this entity in proper order.
        '''
        return [getattr(self,k) for k in self._sa_class_manager.mapper.c.keys()]