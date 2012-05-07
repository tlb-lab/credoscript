import unittest
from collections import Iterable

from sqlalchemy import exc
from sqlalchemy.orm import Query
from sqlalchemy.orm.dynamic import AppenderQuery
from sqlalchemy.orm.collections import MappedCollection

from credoscript.models import Residue
from credoscript.mixins import Pagination

class CredoAdaptorTestCase(unittest.TestCase):
    """
    """
    def assertPagination(self):
        """
        Tests if the adaptor class has the necessary attributes to support
        pagination.
        """
        assert hasattr(self.adaptor, 'paginate') and hasattr(self.adaptor, 'per_page'), "the adaptor class does not support pagination."

    def assertSingleResult(self, method, *args):
        """
        Tests if the method returns the correct single entity as result (or None).
        """
        result = getattr(self.adaptor, method)(*args)

        assert result is None or isinstance(result, self.expected_entity), "method {} does not return the correct result.".format(method)

    def assertPaginatedResult(self, method, *args, **kwargs):
        """
        """
        # this should return the result as a list of entities
        result = getattr(self.adaptor, method)(*args, **kwargs)
        assert all(isinstance(obj, self.expected_entity) for obj in result), "{} does not return the correct entity type.".format(method)

        count = len(result)

        # this should return a query instance
        result = getattr(self.adaptor, method)(*args, dynamic=True, **kwargs)
        self.assertIsInstance(result, Query, "{} does not support dynamic results.".format(method))

        # this should return a Pagination object
        self.adaptor.paginate = True
        result = getattr(self.adaptor, method)(*args, page=1, per_page=100, **kwargs)

        self.assertIsInstance(result, Pagination, "{} does not support pagination.".format(method))
        self.assertEqual(result.total, count)

        #
        if count > 100:
            self.assertEqual(len(result.items), 100)

        self.adaptor.paginate = False

    def assertPaginatedSimilarityHits(self, method, *expr, **kwargs):
        """
        """
        # this should return a list of tuples in the form (similarity, entity)
        result = getattr(self.adaptor, method)(*expr, **kwargs)
        assert all(isinstance(ent, self.expected_entity) and isinstance(sim, float)
                   for ent, sim in result), "{} does not return the correct result tuple.".format(method)

        result = getattr(self.adaptor, method)(*expr, dynamic=True, **kwargs)
        self.assertIsInstance(result, Query, "{} does not support dynamic results.".format(method))

        # this should return a Pagination object
        self.adaptor.paginate = True
        result = getattr(self.adaptor, method)(*expr, page=1, **kwargs)

        self.assertIsInstance(result, Pagination, "{} does not support pagination.".format(method))
        self.adaptor.paginate = False

class CredoEntityTestCase(unittest.TestCase):
    """
    """
    def assertMappedCollection(self, entity, prop):
        """
        """
        # test first if the attribute exists at all
        try:
            attr = getattr(entity, prop)
        except AttributeError:
            raise AssertionError("entity {} does not have a {} attribute."
                                 .format(entity.__class__, prop))

        self.assertIsInstance(attr, MappedCollection)

    def assertOneToOne(self, entity, prop, other):
        """
        the given property name of the entity must return a specific entity or
        None.
        """
        # test first if the attribute exists at all
        try:
            attr = getattr(entity, prop)
        except AttributeError:
            raise AssertionError("entity {} does not have a {} attribute."
                                 .format(entity.__class__, prop))

        # now check for one-to-one relationship
        assert attr is None or isinstance(attr, other), "{} is not a valid one-to-one relationship.".format(prop)

    def assertDynamicRelationship(self, entity, prop, other):
        """
        the given property name of the entity must return a query. Only one-to-many
        relationships should be dynamic.
        """
        # test first if the attribute exists at all
        try:
            query = getattr(entity, prop)
        except AttributeError:
            raise AssertionError("entity {} does not have a {} attribute."
                                 .format(entity.__class__, prop))

        # now check for one-to-many relationship
        assert isinstance(query, Query), "{} is not a dynamic relationship that returns a query.".format(prop)

        try:
            result = query.all()

        # catch possible errors in the query is badly written
        except exc.ProgrammingError as error:
            raise AssertionError("dynamic relationship {} of entity {} uses an "
                                 "invalid query: {}".format(prop, entity.__class__, error))

        # check that result has the appropriate type
        else:
            assert all(isinstance(obj, other) for obj in result), "{} does not return the correct entity type.".format(prop)

    def assertValidSIFt(self, entity, method, *expr, **kwargs):
        """
        """
        result = getattr(entity, method)(*expr, **kwargs)

        for row in result:
            residue, sift = row[0], row[1:]
            self.assertIsInstance(residue, Residue)
            self.assertEqual(len(sift), 13)