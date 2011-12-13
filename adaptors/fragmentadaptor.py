from sqlalchemy.sql.expression import and_, text

from credoscript import session

class FragmentAdaptor(object):
    '''
    '''
    def __init__(self):
        '''
        '''
        self.query = session.query(Fragment)

    def fetch_by_fragment_id(self, fragment_id):
        '''
        '''
        return self.query.get(fragment_id)

    def fetch_all_children(self, fragment_id):
        '''
        '''
        return self.query.join(
            (FragmentHierarchy, FragmentHierarchy.child_id==Fragment.fragment_id)
            ).filter(FragmentHierarchy.parent_id==fragment_id).all()

    def fetch_all_parents(self, fragment_id):
        '''
        '''
        subquery = session.query(FragmentHierarchy.het_id,
                                 func.max(FragmentHierarchy.order_child).label('child')
                                 ).filter(FragmentHierarchy.child_id==fragment_id
                                          ).group_by(FragmentHierarchy.het_id).subquery()

        return session.query(Fragment).join(
            (FragmentHierarchy, FragmentHierarchy.parent_id==Fragment.fragment_id),
            (subquery, and_(subquery.c.het_id==FragmentHierarchy.het_id,
                            subquery.c.child==FragmentHierarchy.order_child))
            ).filter(FragmentHierarchy.child_id==fragment_id).all()

    def fetch_all_descendants(self, fragment_id):
        '''
        '''
        statement = text("""
                        WITH    RECURSIVE descendants(fragment_id)
                        AS      (
                                SELECT  f.*
                                FROM    pdbchem.fragment_hierarchies h
                                JOIN    pdbchem.fragments f ON f.fragment_id = h.child_id
                                WHERE   h.parent_id = :fragment_id
                                UNION
                                SELECT  f.*
                                FROM    pdbchem.fragments f,
                                        pdbchem.fragment_hierarchies h,
                                        descendants d
                                WHERE   h.child_id = f.fragment_id
                                        AND h.parent_id = d.fragment_id
                                        AND h.child_id IS NOT NULL
                                )
                        SELECT      *
                        FROM        descendants
                        ORDER BY    1 DESC
                        """)

        return self.query.from_statement(statement).params(fragment_id=fragment_id).all()

    def fetch_all_leaves(self, fragment_id):
        '''
        '''
        statement = text("""
                        WITH    RECURSIVE descendants(fragment_id)
                        AS      (
                                SELECT  f.*
                                FROM    pdbchem.fragment_hierarchies h
                                JOIN    pdbchem.fragments f ON f.fragment_id = h.child_id
                                WHERE   h.parent_id = :fragment_id
                                UNION
                                SELECT  f.*
                                FROM    pdbchem.fragments f,
                                        pdbchem.fragment_hierarchies h,
                                        descendants d
                                WHERE   h.child_id = f.fragment_id
                                        AND h.parent_id = d.fragment_id
                                        AND h.child_id IS NOT NULL
                                )
                        SELECT      *
                        FROM        descendants
                        WHERE       is_terminal
                        ORDER BY    1 DESC
                        """)

        return self.query.from_statement(statement).params(fragment_id=fragment_id).all()

    def fetch_all_by_het_id(self, het_id, *expressions):
        '''
        '''
        return self.query.join(
            (ChemCompFragment, ChemCompFragment.fragment_id==Fragment.fragment_id)
            ).filter(and_(ChemCompFragment.het_id==het_id, *expressions)).all()

from ..models.fragment import Fragment
from ..models.chemcompfragment import ChemCompFragment