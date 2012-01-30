from sqlalchemy.sql.expression import and_, text

from credoscript.mixins import PathAdaptorMixin

class AromaticRingAdaptor(PathAdaptorMixin):
    '''
    '''
    def __init__(self):
        self.query = AromaticRing.query
       
    def fetch_by_aromatic_ring_id(self, aromatic_ring_id):
        '''
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
        '''
        return self.query(AromaticRing).get(aromatic_ring_id)

    def fetch_all_by_biomolecule_id(self, biomolecule_id, *expressions):
        '''
        Returns all `AromaticRing` objects that can be found in the `Biomolecule`
        with the given biomolecule_id in contact with another entity.

        Parameters
        ----------
        biomolecule_id : int
            `Ligand` identifier.
        *expressions : BinaryExpressions, optional
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
        '''
        query = self.query(AromaticRing).filter(
            and_(AromaticRing.biomolecule_id==biomolecule_id, *expressions))

        return query.all()

    def fetch_all_by_ligand_id(self, ligand_id, *expressions):
        '''
        Returns all `AromaticRing` objects that are part of the `Ligand` with the
        given ligand_id.

        Parameters
        ----------
        ligand_id : int
            `Ligand` identifier.
        *expressions : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Joins
        -----
        AromaticRing, Residue, LigandComponent

        Returns
        -------
        contacts : list
            List of `AromaticRing` objects.

         Examples
        --------
        >>> AromaticRingAdaptor().fetch_all_by_ligand_id(1)
        <Contact()>
        '''
        query = self.query(AromaticRing).join(
            (Residue, Residue.residue_id==AromaticRing.residue_id),
            (LigandComponent, LigandComponent.residue_id==Residue.residue_id)
            ).filter(and_(LigandComponent.ligand_id==ligand_id, *expressions))

        return query.all()

from ..models.aromaticring import AromaticRing
from ..models.residue import Residue
from ..models.ligandcomponent import LigandComponent