"""
This Mixin defines methods that use the ptree PostgreSQL extension. The ptree
extension is essentially the same as the ltree contrib module but uses a different
delimiter '/' and allows '-' to represent negative numbers. Documentation on how
to use the ptree methods can be found in the PostgreSQL documentation of the ltree
module (http://www.postgresql.org/docs/current/static/ltree.html).
"""

from sqlalchemy.orm import deferred
from sqlalchemy.sql.expression import and_

class PathMixin(object):
    '''
    This Mixin is used to add methods for the ptree path attribute of some CREDO
    entities. Paths in CREDO always start with the tree <PDB>/<ASSEMBLY SERIAL>/
    <PDB CHAIN ID>/<RESNUM>`<RESNAME>.
    '''
    @classmethod
    def pmatches(self, pquery):
        '''
        Returns "ptree matches pquery" as SQL expression.
        
        Parameters
        ----------
        pquery : str
            Query string in ltree-compatible syntax, e.g. 1GQF/1/A/HIS`402F.
        '''
        return self.path.op('~')(pquery)
    
    @classmethod
    def pancestor(self, pquery):
        '''
        Returns "is left argument an ancestor of right (or equal)?" as SQL expression.
        '''
        return self.path.op('@>')(pquery)
    
    @classmethod
    def pdescendant(self, pquery):
        '''
        Returns "is left argument a descendant of right (or equal)?" as SQL expression.
        '''
        return self.path.op('<@')(pquery)

class PathAdaptorMixin(object):
    '''
    Adds method for fetching CREDO entities via the (ptree) path attribute.
    '''
    def fetch_all_by_path_match(self, pquery, *expressions):
        '''
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
        '''
        query = self.query.filter("path ~ :pquery").params(pquery=pquery)
        query = query.filter(and_(*expressions))
        
        return query.all()
    
    def fetch_all_path_ancestors(self, ptree, *expressions):
        '''
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
        '''
        query = self.query.filter("path @> :ptree").params(ptree=ptree)
        query = query.filter(and_(*expressions))
        
        return query.all()    
    
    def fetch_all_path_descendants(self, ptree, *expressions):
        '''
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
        '''
        query = self.query.filter("path <@ :ptree").params(ptree=ptree)
        query = query.filter(and_(*expressions))
        
        return query.all()