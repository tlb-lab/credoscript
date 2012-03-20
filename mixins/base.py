from math import ceil

# workaround for Python < 2.7
# the __meta__ attribute of all mapped classes will have the wrong order though!
try: from collections import OrderedDict
except ImportError: OrderedDict = dict

from sqlalchemy.orm import class_mapper, Query

from credoscript import Session

class ClassProperty(property):
    """
    Analogous to the property() function but for class methods.
    From http://stackoverflow.com/questions/128573/using-property-on-classmethods
    """
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()

class Pagination(object):
    """
    Internal helper class returned by BaseQuery.paginate.  You
    can also construct it from any other SQLAlchemy query object if you are
    working with other libraries.  Additionally it is possible to pass None
    as query object in which case the prev and next will no longer work.
    
    Adapted from the Flask-SQLAlchemy extension (http://packages.python.org/Flas
    k-SQLAlchemy/api.html#flaskext.sqlalchemy.Pagination) 
    """
    def __init__(self, query, page, per_page, total, items):
        self.query = query
        self.page = page
        self.per_page = per_page
        self.total = total
        self.items = items

    def __iter__(self):
        """
        Returns an iterator over all the pages.
        """
        for page in xrange(1, self.pages+1):
            yield self.query.paginate(page, self.per_page)

    @property
    def pages(self):
        """
        The total number of pages.
        """
        return int(ceil(self.total / float(self.per_page)))

    def prev(self):
        """
        Returns Pagination object for the previous page.
        """
        assert self.query is not None, 'a query object is required for this method to work'
        return self.query.paginate(self.page - 1, self.per_page)

    @property
    def prev_num(self):
        """
        Number of the previous page.
        """
        return self.page - 1

    @property
    def has_prev(self):
        """
        True if a previous page exists
        """
        return self.page > 1

    def next(self):
        """
        Returns a Pagination object for the next page.
        """
        return self.query.paginate(self.page + 1, self.per_page)

    @property
    def has_next(self):
        """
        True if a next page exists.
        """
        return self.page < self.pages

    @property
    def next_num(self):
        """
        Number of the next page
        """
        return self.page + 1

class BaseQuery(Query):
    """
    Base query that will be attached to every model in the credoscript API.
    
    Adapted from the Flask-SQLAlchemy extension (http://packages.python.org/Flas
    k-SQLAlchemy/api.html#flaskext.sqlalchemy.Pagination) 
    """
    def paginate(self, page=1, per_page=10):
        """
        """
        items = self.limit(per_page).offset((page - 1) * per_page).all()
        
        return Pagination(self, page, per_page, self.count(), items)

class Base(object):
    """
    Declarative base model that is inherited by all CREDO models.
    """
    # automatically reflect the table
    __table_args__ = {'autoload':True}
    
    # attach a query object to every model that queries itself
    query = Session.query_property(BaseQuery)
    
    @ClassProperty
    @classmethod
    def __meta__(cls):
        """
        Returns the metadata information of this class as ordered dictionary.
        """
        mapper = class_mapper(cls)
        meta = OrderedDict()
        
        # get the column data type for every column name
        # this has to be done in a for loop to catch the rror that might occur if
        # the entity has data type stemming from an extension
        for key in mapper.c.keys():
            try: meta[str(key)] = str(mapper.c[key].type)
            except NotImplementedError: meta[str(key)] = "CUSTOM"
        
        return meta
    
    @property 
    def __data__(self):
        """
        Returns a list of values for this entity in proper order.
        """
        return [getattr(self,k) for k in self._sa_class_manager.mapper.c.keys()]
    
    @property
    def _pkey(self):
        """
        Returns the value of the primary key. Also works for composite keys.
        """
        return tuple(getattr(self,c.name) for c in self._sa_class_manager.mapper.primary_key)

    @property
    def _entity_id(self):
        """
        Returns the first column of the primary key as scalar value. Used in the
        PyMOL API.
        """
        return self._pkey[0]