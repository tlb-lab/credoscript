import functools
from math import ceil

from sqlalchemy.orm import Query

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
    def paginate(self, page=1, per_page=100):
        """
        """
        items = self.limit(per_page).offset((page - 1) * per_page).all()

        # remove unncessary ORDER BY clause from counting
        count = self.order_by(False).count()

        return Pagination(self, page, per_page, count, items)

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
        mapper = cls.__mapper__
        meta = []

        # get the column data type for every column name
        # this has to be done in a for loop to catch the error that might occur
        # if the entity has data type stemming from an extension
        for key in mapper.c.keys():
            try: meta.append((str(key), str(mapper.c[key].type)))
            except NotImplementedError: meta.append((str(key), "CUSTOM"))

        return meta

    def _repr_list_(self):
        """
        Returns a list of values for this entity in proper order.
        """
        return [getattr(self,k) for k in self._sa_class_manager.mapper.c.keys()]

    def _repr_dict_(self):
        """
        Returns a dictionary (column name, data) representation of this entity.
        """
        return dict((k, getattr(self,k))
                    for k in self._sa_class_manager.mapper.c.keys())

    def _repr_html_(self):
        """
        Returns a HTML representation (table) of the entity. Only used in IPython
        notebooks.
        """
        data = self._repr_dict_().items()
        rows = ''.join("<tr><th>{}</th><td>{}</td></tr>".format(k,v) for k,v in data)
        table = "<table>{}</table>".format(rows)

        return table

    @property
    def __data__(self):
        """
        Returns a list of values for this entity in proper order.
        """
        return self._repr_list_()

    @property
    def _pkey(self):
        """
        Returns the value of the primary key. Also works for composite keys.
        """
        return tuple(getattr(self, c.name) for c in self.__mapper__.primary_key)

    @property
    def _entity_id(self):
        """
        Returns the first column of the primary key as scalar value. Used in the
        PyMOL API.
        """
        return self._pkey[0]

def paginate(func):
    """
    """
    @functools.wraps(paginate)
    def wrapper(self, *args, **kwargs):
        query = func(self, *args, **kwargs)

        # add an orderby clause if given to the decorated function
        orderby = kwargs.get('orderby')
        if orderby:
            query = query.order_by(*orderby)

        # return query to simulate a dynamic relationship
        if self.dynamic:
            return query

        # return a pagination object
        elif self.paginate:
            page = kwargs.get('page',1)
            return query.paginate(page=page, per_page=self.per_page)

        else:
            return query.all()

    return wrapper
