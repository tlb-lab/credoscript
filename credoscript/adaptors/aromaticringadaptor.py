from sqlalchemy.sql.expression import and_

from credoscript.mixins import PathAdaptorMixin
from credoscript.mixins.base import paginate

class AromaticRingAdaptor(PathAdaptorMixin):
    """
    """
    def __init__(self, dynamic=False, paginate=False, per_page=100):
        self.query = AromaticRing.query
        self.dynamic = dynamic
        self.paginate = paginate
        self.per_page = per_page

    def fetch_by_aromatic_ring_id(self, aromatic_ring_id):
        """
        Parameters
        ----------
        aromatic_ring_id : int
            Primary key of the `Contact` in CREDO.

        Returns
        -------
        AromaticRing
            CREDO `AromaticRing` object having this aromatic_ring_id as primary key.

        Examples
        --------
        >>> AromaticRingAdaptor().fetch_by_aromatic_ring_id(1)
        <AromaticRing(1)>
        """
        return self.query.get(aromatic_ring_id)

    @paginate
    def fetch_all_by_biomolecule_id(self, biomolecule_id, *expr, **kwargs):
        """
        Returns all `AromaticRing` objects that can be found in the `Biomolecule`
        with the given biomolecule_id in contact with another entity.

        Parameters
        ----------
        biomolecule_id : int
            `Ligand` identifier.
        *expr : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Joins
        -----
        AromaticRing

        Returns
        -------
        contacts : list
            List of `AromaticRing` objects.

         Examples
        --------
        >>> AromaticRingAdaptor().fetch_all_by_biomolecule_id(1)
        <Contact()>
        """
        query = self.query.filter(and_(AromaticRing.biomolecule_id==biomolecule_id, *expr))

        return query

    @paginate
    def fetch_all_by_ligand_id(self, ligand_id, *expr, **kwargs):
        """
        Returns all `AromaticRing` objects that are part of the `Ligand` with the
        given ligand_id.

        Parameters
        ----------
        ligand_id : int
            `Ligand` identifier.
        *expr : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Joins
        -----
        AromaticRing, LigandComponent

        Returns
        -------
        contacts : list
            List of `AromaticRing` objects.

         Examples
        --------
        >>> AromaticRingAdaptor().fetch_all_by_ligand_id(1)
        <Contact()>
        """
        query = self.query.join(LigandComponent,
                                LigandComponent.residue_id==AromaticRing.residue_id)
        query = query.filter(and_(LigandComponent.ligand_id==ligand_id, *expr))

        return query

from ..models.aromaticring import AromaticRing
from ..models.ligandcomponent import LigandComponent
