from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import and_, func, or_, text

from credoscript import Session
from credoscript.util import requires
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
    def fetch_all_by_domain_id(self, domain_id, *expr, **kwargs):
        """
        Returns all fragments that are in contact with the protein domain having
        the specified primary key.

        Parameters
        ----------
        domain_id : int
            Primary key of the CREDO protein domain.
        *expr : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried entities
        ----------------
        Fragment, LigandFragment, Ligand, BindingSiteDomain

        Returns
        -------
        fragments : list
            fragments that are in contact with the protein domain having the
            specified primary key.
        """
        query = self.query.join('LigandFragments', 'Ligand', 'BindingSiteDomains')
        query = query.filter(and_(BindingSiteDomain.domain_id==domain_id, *expr))

        return query.distinct()

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

    @requires.rdkit_catridge
    @paginate
    def fetch_all_by_sim(self, smi, *expr, **kwargs):
        """
        Returns all fragments that match the given SMILES string with at
        least the given similarity threshold using chemical fingerprints.

        Parameters
        ----------
        smi : str
            The query rdmol in SMILES format.
        threshold : float, default=0.5
            The similarity threshold that will be used for searching.
        fp : {'circular','atompair','torsion','maccs','layered','avalon'}
            RDKit fingerprint type to be used for similarity searching.
        *expr : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried Entities
        ----------------
        Fragments, FragmentRDFP

        Returns
        -------
        hits : list
            List of tuples in the form (Fragment, similarity)

        Examples
        --------
        >>> #PENDING

        Requires
        --------
        .. important:: `RDKit  <http://www.rdkit.org>`_ PostgreSQL cartridge.
        """
        
        session = Session()

        threshold = kwargs.get('threshold', 0.5)
        metric = kwargs.get('metric', 'tanimoto')
        fp = kwargs.get('fp', 'circular')

        if fp == 'circular':
            query = func.rdkit.morganbv_fp(smi,2).label('queryfp')
            target = FragmentRDFP.circular_fp

        elif fp == 'torsion':
            query = func.rdkit.torsionbv_fp(smi).label('queryfp')
            target = FragmentRDFP.torsion_fp

        elif fp == 'atompair':
            query = func.rdkit.atompairbv_fp(smi).label('queryfp')
            target = FragmentRDFP.atompair_fp
            
        elif fp == 'maccs':
            query = func.rdkit.maccs_fp(smi).label('queryfp')
            target = FragmentRDFP.maccs_fp
            
        elif fp == 'layered':
            query = func.rdkit.layered_fp(smi).label('queryfp')
            target = FragmentRDFP.layered_fp
        
        elif fp == 'avalon':
            query = func.rdkit.avalon_fp(smi).label('queryfp')
            target = FragmentRDFP.avalon_fp
          
        else:
            msg = "The fingerprint type [{0}] does not exist.".format(fp)
            raise RuntimeError(msg)

        # set the similarity threshold for the index
        if metric == 'tanimoto':
            session.execute(text("SET rdkit.tanimoto_threshold=:threshold").execution_options(autocommit=True).params(threshold=threshold))
            sim_thresh = func.current_setting('rdkit.tanimoto_threshold').label('sim_thresh')

            similarity = func.rdkit.tanimoto_sml(query, target).label('similarity')
            index = func.rdkit.tanimoto_sml_op(query,target)
        elif metric == 'dice':
            session.execute(text("SET rdkit.dice_threshold=:threshold").execution_options(autocommit=True).params(threshold=threshold))
            sim_thresh = func.current_setting('rdkit.dice_threshold').label('sim_thresh')

            similarity = func.rdkit.dice_sml(query, target).label('similarity')
            index = func.rdkit.dice_sml_op(query,target)
            
            
        query = self.query.add_columns(similarity, sim_thresh)
        query = query.join('RDFP').filter(and_(index, *expr))
        query = query.order_by('similarity DESC')
        
        if kwargs.get('limit'):
            query = query.limit(kwargs['limit']) #.all(

        #print query.statement
        
        results = query.all()
        #session.close()

        return results # query

    
    @paginate
    def fetch_all_by_trgm_sim(self, smiles, *expr, **kwargs):
        """
        Returns all fragments that are similar to the given SMILES string
        using trigam similarity (similar to LINGO).

        Parameters
        ----------
        threshold : float, default=0.6
            Similarity threshold that will be used for searching.
        limit : int, default=25
            Maximum number of hits that will be returned.

        Returns
        -------
        resultset : list
            List of tuples (Fragment, similarity) containing the chemical components
            and the calculated trigram similarity.

        Queried Entities
        ----------------
        Fragment

        Examples
        --------
        >>>> FragmentAdaptor().fetch_all_by_trgm_sim('Cc1ccc(cc1Nc2nccc(n2)c3cccnc3)NC(=O)c4ccc(cc4)CN5CC[NH+](CC5)C')
        [(<Fragment(STI)>, 0.883721), (<Fragment(NIL)>, 0.73913),
        (<Fragment(PRC)>, 0.738095), (<Fragment(406)>, 0.666667),
        (<Fragment(J07)>, 0.604167), (<Fragment(AD5)>, 0.6),
        (<Fragment(AAX)>, 0.6), (<Fragment(VX6)>, 0.6)]

        Requires
        --------
        .. important:: `pg_trgm  <http://www.postgresql.org/docs/current/static/pgtrgm.html>`_ PostgreSQL extension.
        """
        session = Session()

        threshold = kwargs.get('threshold', 0.6)

        # SET THE SIMILARITY THRESHOLD FOR THE INDEX
        session.execute(text("SELECT set_limit(:threshold)").execution_options(autocommit=True).params(threshold=threshold))

        similarity = func.similarity(Fragment.ism, smiles).label('similarity')
        sim_thresh = func.show_limit().label('sim_thresh')

        query = self.query.add_columns(similarity, sim_thresh)
        query = query.filter(and_(Fragment.like(smiles), *expr))

        # KNN-GIST
        query = query.order_by(Fragment.ism.op('<->')(smiles))

        if kwargs.get('limit'):
            query = query.limit(kwargs['limit'])

        results = query.all()
        #session.close()

        return results #query

from ..models.chemcomp import ChemComp
from ..models.fragment import Fragment
from ..models.fragment_rdkit import FragmentRDMol, FragmentRDFP
from ..models.ligandfragment import LigandFragment
from ..models.fragmenthierarchy import FragmentHierarchy
from ..models.chemcompfragment import ChemCompFragment
from ..models.bindingsite import BindingSiteDomain
