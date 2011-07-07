from sqlalchemy.util import OrderedDict

class Model(object):
    '''
    Abstract class for the CREDO Models.
    '''
    def __eq__(self, other):
        '''
        '''
        return isinstance(other, self.__class__) and self._pkey == other._pkey

    def __ne__(self, other):
        '''
        '''
        return not self == other

    def __lt__(self, other):
        '''
        '''
        return isinstance(other, self.__class__) and self._pkey < other._pkey

    def __le__(self, other):
        '''
        '''
        return isinstance(other, self.__class__) and self._pkey <= other._pkey

    def __ge__(self, other):
        '''
        '''
        return isinstance(other, self.__class__) and self._pkey >= other._pkey

    def __gt__(self, other):
        '''
        '''
        return isinstance(other, self.__class__) and self._pkey > other._pkey

    def __hash__(self):
        '''
        '''
        return hash(self._pkey)

    @property
    def _pkey(self):
        '''
        Returns the value of the primary key. Also works for composite keys.
        '''
        return tuple(self.__dict__[c.name] for c in self._sa_class_manager.mapper.primary_key)

    @property
    def _entity_id(self):
        '''
        '''
        return self._pkey[0]

    @property
    def _meta(self):
        '''
        Returns the metadata information about this entity.
        '''
        return OrderedDict([(str(k), str(c.type)) for k,c in self._sa_class_manager.mapper.c._data.items()])

    @property
    def _data(self):
        '''
        Returns a list of values for this entity in proper order.
        '''
        return [self.__dict__[k] for k in self._sa_class_manager.mapper.c.keys()]