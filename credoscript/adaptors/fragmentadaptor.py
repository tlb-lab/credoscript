from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import and_, func, or_

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
        Returns all fragments that are derived from the given chemical component
        HET-ID.
        """
        query = self.query.join(ChemCompFragment,
                                ChemCompFragment.fragment_id==Fragment.fragment_id)

        query = query.filter(and_(ChemCompFragment.het_id==het_id, *expr))

        return query

    @paginate
    def fetch_all_children(self, fragment_id, *expr, **kwargs):
        """
        Returns all fragments that are derived from this fragment through RECAP.
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
        subquery = FragmentHierarchy.query.with_entities(FragmentHierarchy.het_id,
                                                         func.max(FragmentHierarchy.order_child).label('child'))
        subquery = subquery.filter(FragmentHierarchy.child_id==fragment_id)
        subquery = subquery.group_by(FragmentHierarchy.het_id).subquery()

        query = self.query.join(FragmentHierarchy,
                                FragmentHierarchy.parent_id==Fragment.fragment_id)
        query = query.join(subquery, and_(subquery.c.het_id==FragmentHierarchy.het_id,
                                          subquery.c.child==FragmentHierarchy.order_child))
        query = query.filter(FragmentHierarchy.child_id==fragment_id)

        return query.distinct()

    @paginate
    def fetch_all_descendants(self, fragment_id, *expr, **kwargs):
        """
        Returns all the descending fragments of the fragment with the given
        fragment_id using an recursive SQL query.
        """
        # query part that will be used in both parts of the recursive query
        query = Fragment.query.with_entities(Fragment.fragment_id)
        query = query.join(FragmentHierarchy, FragmentHierarchy.child_id==Fragment.fragment_id)

        # fragment_id is the recursive term
        descendants = query.filter(FragmentHierarchy.parent_id==fragment_id)
        descendants = descendants.cte(name="descendants", recursive=True)

        # alias is necessary to reference to the statement in the recursive part
        desc_alias = aliased(descendants, name="d")

        # recursive part
        end = query.join(desc_alias, desc_alias.c.fragment_id==FragmentHierarchy.parent_id)
        end = end.filter(FragmentHierarchy.child_id!=None)
        descendants = descendants.union(end)

        # Join the recursive statement against the fragments table to get all
        # the fragment entities and add optional filter expressions
        query = self.query.join(descendants, Fragment.fragment_id==descendants.c.fragment_id)
        query = query.filter(and_(*expr)).order_by(Fragment.fragment_id.asc())

        return query

    def fetch_all_leaves(self, fragment_id, *expr, **kwargs):
        """
        Returns only the terminal (leaf) fragments of the fragment with the
        given fragment_id.
        """
        return self.fetch_all_descendants(fragment_id, Fragment.is_terminal==True,
                                          *expr, **kwargs)

    @paginate
    def fetch_all_having_xbonds(self, *expr, **kwargs):
        """
        Returns all fragments that form halogen bonds in CREDO.

        Parameters
        ----------
        *expr : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried entities
        ----------------
        Fragment, LigandFragment

        Returns
        -------
        fragments : list
            fragments that form halogen bonds.
        """
        query = self.query.join('LigandFragments')
        query = query.filter(and_(LigandFragment.num_xbond>0, *expr))

        return query.distinct()

    @paginate
    def fetch_all_having_metal_complexes(self, *expr, **kwargs):
        """
        Returns all ligand fragments that form metal complexes.

        Parameters
        ----------
        *expr : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried entities
        ----------------
        Fragment, LigandFragment

        Returns
        -------
        fragments : list
            fragments that form metal complexes.
        """
        query = self.query.join('LigandFragments')
        query = query.filter(and_(LigandFragment.num_metal_complex>0, *expr))

        return query.distinct()

    @paginate
    def fetch_all_fragment_sets(self, *expr, **kwargs):
        """
        Returns a set of fragments that can be found as a RECAP fragment in other
        chemical components and that can also be found in CREDO interacting with
        a protein through electrostatic interactions.

        Parameters
        ----------
        *expr : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried entities
        ----------------
        Fragment, ChemCompFragment, ChemComp, LigandFragment

        Returns
        -------
        fragments : list
            A list of tuples in the form (Fragment, fragment HET-ID, number of
            chemical components that contain the fragment).
        """
        query = self.query.add_columns(ChemComp.het_id)
        query = query.join("ChemCompFragments","ChemComp")
        query = query.join("LigandFragments")

        query = query.filter(and_(ChemComp.is_fragment==True,
                                  ChemComp.is_lig_in_credo==True,
                                  ChemCompFragment.is_root==True,
                                  LigandFragment.num_covalent==0,
                                  Fragment.is_shared==True,
                                  or_(LigandFragment.num_hbond>0,
                                      LigandFragment.num_xbond>0,
                                      LigandFragment.num_ionic>0,
                                      LigandFragment.num_weak_hbond>0,
                                      LigandFragment.num_carbonyl>0),
                                  *expr))

        fragments = query.distinct().cte(name="fragments")

        query = self.query.select_from(fragments)
        query = query.add_columns(fragments.c.het_id.label("fragment_het_id"),
                                  func.count(ChemCompFragment.het_id).label("num_chem_comps"))

        query = query.join(ChemCompFragment, ChemCompFragment.fragment_id==fragments.c.fragment_id)
        query = query.filter(fragments.c.het_id!=ChemCompFragment.het_id)
        query = query.group_by(fragments).order_by("num_chem_comps DESC")

        return query

from ..models.chemcomp import ChemComp
from ..models.fragment import Fragment
from ..models.ligandfragment import LigandFragment
from ..models.fragmenthierarchy import FragmentHierarchy
from ..models.chemcompfragment import ChemCompFragment
