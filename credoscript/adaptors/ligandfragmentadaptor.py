from sqlalchemy.sql.expression import and_

from credoscript.mixins.base import paginate

class LigandFragmentAdaptor(object):
    """
    """
    def __init__(self, dynamic=False, paginate=False, per_page=100):
        self.query = LigandFragment.query
        self.dynamic = dynamic
        self.paginate = paginate
        self.per_page = per_page

    def fetch_by_ligand_fragment_id(self, ligand_fragment_id):
        """
        """
        return self.query.get(ligand_fragment_id)

    @paginate
    def fetch_all_by_ligand_id(self, ligand_id):
        """
        Returns all ligand fragments that are part of the ligand with the given
        ligand_id.
        """
        return self.query.filter_by(ligand_id=ligand_id)

    @paginate
    def fetch_all_having_xbonds(self, *expr, **kwargs):
        """
        Returns all ligand fragments that form halogen bonds.

        Parameters
        ----------
        *expr : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried entities
        ----------------
        LigandFragment

        Returns
        -------
        ligand fragments : list
            ligand fragments that form halogen bonds.
        """
        return self.query.filter(and_(LigandFragment.num_xbond>0, *expr))

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
        LigandFragment

        Returns
        -------
        ligand fragments : list
            ligand fragments that form metal complexes.
        """
        return self.query.filter(and_(LigandFragment.num_metal_complex>0, *expr))

from ..models.ligandfragment import LigandFragment
