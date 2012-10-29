from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import and_, func

from credoscript import Session
from credoscript.mixins.base import paginate

class FragmentAdaptor(object):
    """
    """
    def __init__(self, dynamic=False, paginate=False, per_page=100):
        self.query = Fragment.query
        self.dynamic = dynamic
        self.paginate = paginate
        self.per_page = per_page

    def fetch_by_fragment_id(self, fragment_id):
        """
        """
        return self.query.get(fragment_id)

    @paginate
    def fetch_all_by_het_id(self, het_id, *expr, **kwargs):
        """
        """
        query = self.query.join(ChemCompFragment,
                                ChemCompFragment.fragment_id==Fragment.fragment_id)

        query = query.filter(and_(ChemCompFragment.het_id==het_id, *expr))

        return query

    @paginate
    def fetch_all_children(self, fragment_id, *expr, **kwargs):
        """
        """
        query = self.query.join(FragmentHierarchy,
                                FragmentHierarchy.child_id==Fragment.fragment_id)
        query = query.filter(and_(FragmentHierarchy.parent_id==fragment_id,
                                  *expr))

        return query

    @paginate
    def fetch_all_parents(self, fragment_id, *expr, **kwargs):
        """
        """
        session = Session()

        subquery = session.query(FragmentHierarchy.het_id,
                                 func.max(FragmentHierarchy.order_child).label('child')
                                 ).filter(FragmentHierarchy.child_id==fragment_id
                                          ).group_by(FragmentHierarchy.het_id).subquery()

        query = self.query.join(FragmentHierarchy,
                                FragmentHierarchy.parent_id==Fragment.fragment_id)
        query = query.join(subquery, and_(subquery.c.het_id==FragmentHierarchy.het_id,
                                          subquery.c.child==FragmentHierarchy.order_child))
        query = query.filter(FragmentHierarchy.child_id==fragment_id)

        session.close()

        return query.distinct()

    @paginate
    def fetch_all_descendants(self, fragment_id, *expr, **kwargs):
        """
        """
        session = Session()

        descendants = session.query(Fragment.fragment_id)
        descendants = descendants.join(FragmentHierarchy,
                                       FragmentHierarchy.child_id==Fragment.fragment_id)
        descendants = descendants.filter(FragmentHierarchy.parent_id==fragment_id)
        descendants = descendants.cte(name="descendants", recursive=True)

        desc_alias = aliased(descendants, name="d")

        end = session.query(Fragment.fragment_id)
        end = end.join(FragmentHierarchy, FragmentHierarchy.child_id==Fragment.fragment_id)
        end = end.join(desc_alias, desc_alias.c.fragment_id==FragmentHierarchy.parent_id)
        end = end.filter(FragmentHierarchy.child_id!=None)

        descendants = descendants.union(end)

        query = self.query.join(descendants,
                                Fragment.fragment_id==descendants.c.fragment_id)

        query = query.filter(and_(*expr))
        query = query.order_by(Fragment.fragment_id.asc())

        # only return the terminal leaves
        if kwargs.get('leaves', False):
            query = query.filter(Fragment.is_terminal==True)

        session.close()

        return query

    def fetch_all_leaves(self, fragment_id, *expr, **kwargs):
        """
        """
        return self.fetch_all_descendants(fragment_id, *expr, leaves=True, **kwargs)

from ..models.fragment import Fragment
from ..models.fragmenthierarchy import FragmentHierarchy
from ..models.chemcompfragment import ChemCompFragment
