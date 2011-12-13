from sqlalchemy.sql.expression import and_

from credoscript import session

class AtomRingInteractionAdaptor(object):
    '''
    '''
    def __init__(self):
        '''
        '''
        self.query = session.query(AtomRingInteraction)

    def fetch_by_atom_ring_interaction_id(self, atom_ring_interaction_id):
        '''
        Parameters
        ----------
        atom_ring_interaction_id : int
            Primary key of the `Residue` in CREDO.

        Returns
        -------
        Atom
            CREDO `Residue` object having this atom_id as primary key.

        Examples
        --------
        >>> AtomRingInteractionAdaptor().fetch_by_atom_ring_interaction_id(1)

        '''
        return self.query.get(atom_ring_interaction_id)

    def fetch_all_by_biomolecule_id(self, biomolecule_id, *expressions):
        '''
        Returns all the interactions between an atom and an aromatic ring.

        Parameters
        ----------
        biomolecule_id : int
            `Ligand` identifier.
        *expressions : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Joins
        -----
        AtomRingInteraction, AromaticRing

        Returns
        -------
        contacts : list
            List of `AtomRingInteraction` objects.

         Examples
        --------
        >>> AtomRingInteractionAdaptor().fetch_all_by_biomolecule_id(396)
        [<AtomRingInteraction(22271)>, <AtomRingInteraction(22272)>,
         <AtomRingInteraction(22273)>, <AtomRingInteraction(22274)>,
         <AtomRingInteraction(22275)>, <AtomRingInteraction(22276)>,
         <AtomRingInteraction(22277)>]
        '''
        query = self.query(AtomRingInteraction).join('AromaticRing')
        query = query.filter(and_(AromaticRing.biomolecule_id==biomolecule_id, *expressions))

        return query.all()

    def fetch_all_by_ligand_id(self, ligand_id, *expressions):
        '''
        Returns all the interactions between an atom and an aromatic ring.

        Parameters
        ----------
        ligand_id : int
            `Ligand` identifier.
        *expressions : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Joins
        -----
        AtomRingInteraction, AromaticRing

        Returns
        -------
        contacts : list
            List of `AtomRingInteraction` objects.

         Examples
        --------
        >>> AtomRingInteractionAdaptor().fetch_all_by_ligand_id(396)
        [<AtomRingInteraction(22293)>, <AtomRingInteraction(22297)>,
        <AtomRingInteraction(22296)>, <AtomRingInteraction(22292)>,
        <AtomRingInteraction(22298)>, <AtomRingInteraction(22294)>,
        <AtomRingInteraction(22295)>]
        '''
        # ATOM BELONGS TO LIGAND
        atom = self.query.join(
            (Hetatm, Hetatm.atom_id==AtomRingInteraction.atom_id)
            ).filter(and_(Hetatm.ligand_id==ligand_id, *expressions))

        # RING BELONGS TO LIGAND
        ring = self.query.join(
            (AromaticRing, AromaticRing.aromatic_ring_id==AtomRingInteraction.aromatic_ring_id),
            (LigandComponent, LigandComponent.residue_id==AromaticRing.residue_id)
            ).filter(and_(LigandComponent.ligand_id==ligand_id, *expressions))

        return atom.union(ring).all()

from ..models.hetatm import Hetatm
from ..models.ligandcomponent import LigandComponent
from ..models.aromaticring import AromaticRing
from ..models.atomringinteraction import AtomRingInteraction