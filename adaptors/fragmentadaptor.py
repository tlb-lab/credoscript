from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import and_, text

from credoscript import Session

class FragmentAdaptor(object):
    """
    """
    def __init__(self, paginate=False, per_page=100):
        """
        """
        self.paginate = paginate
        self.per_page = per_page
       
    def fetch_by_fragment_id(self, fragment_id):
        """
        """
        return Fragment.query.get(fragment_id)

    def fetch_all_children(self, fragment_id):
        """
        """
        return Fragment.query.join(
            (FragmentHierarchy, FragmentHierarchy.child_id==Fragment.fragment_id)
            ).filter(FragmentHierarchy.parent_id==fragment_id).all()

    def fetch_all_parents(self, fragment_id):
        """
        """
        session = Session()
        
        subquery = session.query(FragmentHierarchy.het_id,
                                 func.max(FragmentHierarchy.order_child).label('child')
                                 ).filter(FragmentHierarchy.child_id==fragment_id
                                          ).group_by(FragmentHierarchy.het_id).subquery()

        parents = Fragment.query.join(FragmentHierarchy, FragmentHierarchy.parent_id==Fragment.fragment_id)
        parents = parents.join(subquery, and_(subquery.c.het_id==FragmentHierarchy.het_id,
                                               subquery.c.child==FragmentHierarchy.order_child))
        parents = parents.filter(FragmentHierarchy.child_id==fragment_id).all()
        
        session.remove()
        
        return parents

    def fetch_all_descendants(self, fragment_id, *expressions, **kwargs):
        """
        WITH    RECURSIVE descendants(fragment_id)
                AS      (
                        SELECT f.*
                          FROM pdbchem.fragments f
                          JOIN pdbchem.fragment_hierarchies h ON h.child_id = f.fragment_id
                         WHERE h.parent_id = :fragment_id
                         UNION
                        SELECT f.*
                          FROM pdbchem.fragments f
                          JOIN pdbchem.fragment_hierarchies h ON h.child_id = f.fragment_id
                          JOIN descendants d ON h.parent_id = d.fragment_id
                         WHERE h.child_id IS NOT NULL
                        )
                SELECT      *
                FROM        descendants
                ORDER BY    1 DESC
        """
        session = Session()
        
        descendants = session.query(Fragment.fragment_id)
        descendants = descendants.join(FragmentHierarchy, FragmentHierarchy.child_id==Fragment.fragment_id)
        descendants = descendants.filter(FragmentHierarchy.parent_id==fragment_id)
        descendants = descendants.cte(name="descendants", recursive=True)

        desc_alias = aliased(descendants, name="d")
        
        end = session.query(Fragment.fragment_id)
        end = end.join(FragmentHierarchy, FragmentHierarchy.child_id==Fragment.fragment_id)
        end = end.join(desc_alias, desc_alias.c.fragment_id==FragmentHierarchy.parent_id)
        end = end.filter(FragmentHierarchy.child_id!=None)
        
        descendants = descendants.union(end)
        
        fragments = Fragment.query.join(descendants,
                                        Fragment.fragment_id==descendants.c.fragment_id)
        
        fragments = fragments.filter(and_(*expressions))
        fragments = fragments.order_by(Fragment.fragment_id.asc())
        
        # only return the terminal leaves
        if kwargs.get('leaves', False):
            fragments = fragments.filter(Fragment.is_terminal==True)
        
        result = fragments.all()
        
        session.remove()
        
        return result

    def fetch_all_leaves(self, fragment_id, *expressions):
        """
        """
        return self.fetch_all_descendants(fragment_id, *expressions, leaves=True)

    def fetch_all_by_het_id(self, het_id, *expressions, **kwargs):
        """
        """
        query = Fragment.query.join(ChemCompFragment,
                                    ChemCompFragment.fragment_id==Fragment.fragment_id)
        
        query = query.filter(and_(ChemCompFragment.het_id==het_id, *expressions))
        
        if self.paginate:
            page = kwargs.get('page',1)
            return query.paginate(page=page, per_page=self.per_page)
            
        else: return query.all()   

from ..models.fragment import Fragment
from ..models.fragmenthierarchy import FragmentHierarchy
from ..models.chemcompfragment import ChemCompFragment