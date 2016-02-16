from sqlalchemy.sql.expression import and_

from credoscript.mixins import PathAdaptorMixin
from credoscript.mixins.base import paginate

class PiGroupAdaptor(PathAdaptorMixin):
    """
    """
    def __init__(self, dynamic=False, paginate=False, per_page=100):
        self.query = PiGroup.query
        self.dynamic = dynamic
        self.paginate = paginate
        self.per_page = per_page

    def fetch_by_pi_id(self, pi_id):
        """
        Parameters
        ----------
        pi_id : int
            Primary key of the `PiGroup` in CREDO.

        Returns
        -------
        PiGroup
            CREDO `PiGroup` object having this pi_id as primary key.

        Examples
        --------
        >>> PiGroupAdaptor().fetch_by_pi_id(1)
        <PiGroup(1)>
        """
        return self.query.get(pi_id)

    @paginate
    def fetch_all_by_biomolecule_id(self, biomolecule_id, *expr, **kwargs):
        """
        Returns all `PiGroup` objects that can be found in the `Biomolecule`
        with the given biomolecule_id in contact with another entity.

        Parameters
        ----------
        biomolecule_id : int
            `Ligand` identifier.
        *expr : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Joins
        -----
        PiGroup

        Returns
        -------
        contacts : list
            List of `PiGroup` objects.

         Examples
        --------
        >>> PiGroupAdaptor().fetch_all_by_biomolecule_id(1)
        <Contact()>
        """
        query = self.query.filter(and_(PiGroup.biomolecule_id==biomolecule_id, *expr))

        return query

    @paginate
    def fetch_all_by_ligand_id(self, ligand_id, *expr, **kwargs):
        """
        Returns all `PiGroup` objects that are part of the `Ligand` with the
        given ligand_id.

        Parameters
        ----------
        ligand_id : int
            `Ligand` identifier.
        *expr : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Joins
        -----
        PiGroup, LigandComponent

        Returns
        -------
        contacts : list
            List of `PiGroup` objects.

         Examples
        --------
        >>> PiGroupAdaptor().fetch_all_by_ligand_id(1)
        <Contact()>
        """
        query = self.query.join(LigandComponent,
                                PiGroup.residue_id == LigandComponent.residue_id)
        query = query.filter(and_(LigandComponent.ligand_id==ligand_id, *expr))

        return query

from ..models.pigroup import PiGroup
from ..models.ligandcomponent import LigandComponent
