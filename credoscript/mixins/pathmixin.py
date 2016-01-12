"""
This Mixin defines methods that use the ptree PostgreSQL extension. The ptree
extension is essentially the same as the ltree contrib module but uses a different
delimiter '/' and allows '-' to represent negative numbers. Documentation on how
to use the ptree methods can be found in the PostgreSQL documentation of the ltree
module (http://www.postgresql.org/docs/current/static/ltree.html).
"""
import re

from sqlalchemy.orm import deferred
from sqlalchemy.sql.expression import and_
from sqlalchemy.types import UserDefinedType
from sqlalchemy.dialects.postgresql.base import ischema_names

from credoscript.mixins.base import paginate

class PTREE(UserDefinedType):
    """Path tree custom type. Not currently used.""" 

    def get_col_spec(self):
        return "ptree"

    def bind_processor(self, dialect):
        def process(value):
            return value
        return process

    def result_processor(self, dialect, coltype):
        def process(value):
            return value
        return process

ischema_names['ptree'] = PTREE


class PathMixin(object):
    """
    This Mixin is used to add methods for the ptree path attribute of some CREDO
    entities. Paths in CREDO always start with the tree <PDB>/<ASSEMBLY SERIAL>/
    <PDB CHAIN ID>/<RESNUM>`<RESNAME>.
    """
    @classmethod
    def pmatches(self, pquery):
        """
        Returns "ptree matches pquery" as SQL expression.

        Parameters
        ----------
        pquery : str
            Query string in ltree-compatible syntax, e.g. 1GQF/1/A/HIS`402F.
        """
        return self.path.op('~')(pquery)

    @classmethod
    def pancestor(self, pquery):
        """
        Returns "is left argument an ancestor of right (or equal)?" as SQL expression.
        """
        return self.path.op('@>')(pquery)

    @classmethod
    def pdescendant(self, pquery):
        """
        Returns "is left argument a descendant of right (or equal)?" as SQL expression.
        """
        return self.path.op('<@')(pquery)

    @property
    def pymolstring(self):
        """
        Returns a PyMOL selection string with the biomolecule identifier removed.
        """
        return '/' + re.sub('/\d+/','//', self.path)
        
    def path_fmt(self, first=0, last=None, **kwargs):
        """
        """
        if not first and not last and not kwargs:
            return self.path
        elif not kwargs:
            path_tokens = self.path.split('/')
            return '/'.join(path_tokens[first:(last or len(path_tokens))])


class PathAdaptorMixin(object):
    """
    Adds method for fetching CREDO entities via the (ptree) path attribute.
    """
    def fetch_by_path(self, path):
        """
        Returns the entity that has the identical path.
        """
        query = self.query.filter_by(path=path)

        return query.first()

    @paginate
    def fetch_all_by_path_match(self, pquery, *expressions, **kwargs):
        """
        Returns all the entities whose path matches the given pquery.

        Parameters
        ----------
        pquery : str
            A regular-expression-like pattern for matching p tree values, e.g.
            1GQF/1/*/HIS`402F.
        *expressions : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Returns
        -------
        matches : list
            All the entities whose path matches the (ptree) path attribute.
        """
        query = self.query.filter("path ~ :pquery").params(pquery=pquery)
        query = query.filter(and_(*expressions))

        return query

    @paginate
    def fetch_all_path_ancestors(self, ptree, *expressions, **kwargs):
        """
        Returns all the entities whose path is an ancestor of the given pquery.

        Parameters
        ----------
        ptree : str
            ptree, e.g. 1GQF/1/A/HIS`402F.
        *expressions : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Returns
        -------
        matches : list
            All the entities whose path is an ancestor of the given ptree.
        """
        query = self.query.filter("path @> :ptree").params(ptree=ptree)
        query = query.filter(and_(*expressions))

        return query

    @paginate
    def fetch_all_path_descendants(self, ptree, *expressions, **kwargs):
        """
        Returns all the entities whose path is a descendant of the given pquery.

        Parameters
        ----------
        ptree : str
            ptree, e.g. 1GQF/1/A/HIS`402F.
        *expressions : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Returns
        -------
        matches : list
            All the entities whose path is a descendant of the given ptree.
        """
        query = self.query.filter("path <@ :ptree").params(ptree=ptree)
        query = query.filter(and_(*expressions))

        return query