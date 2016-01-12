from sqlalchemy.sql.expression import and_, or_

from credoscript.mixins.base import paginate

class AtomRingInteractionAdaptor(object):
    """
    """
    def __init__(self, dynamic=False, paginate=False, per_page=100):
        self.query = AtomRingInteraction.query
        self.dynamic = dynamic
        self.paginate = paginate
        self.per_page = per_page

    def fetch_by_atom_ring_interaction_id(self, atom_ring_interaction_id):
        """
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

        """
        return self.query.get(atom_ring_interaction_id)

    @paginate
    def fetch_all_by_biomolecule_id(self, biomolecule_id, *expressions, **kwargs):
        """
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
        """
        query = self.query.join('AromaticRing')
        query = query.filter(and_(AromaticRing.biomolecule_id==biomolecule_id,
                                  *expressions))

        return query

    @paginate
    def fetch_all_by_ligand_id(self, ligand_id, *expressions, **kwargs):
        """
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
        """
        # ATOM BELONGS TO LIGAND
        atom = self.query.join(
            (Hetatm, Hetatm.atom_id==AtomRingInteraction.atom_id)
            ).filter(and_(Hetatm.ligand_id==ligand_id, *expressions))

        # RING BELONGS TO LIGAND
        ring = self.query.join(
            (AromaticRing, AromaticRing.aromatic_ring_id==AtomRingInteraction.aromatic_ring_id),
            (LigandComponent, LigandComponent.residue_id==AromaticRing.residue_id)
            ).filter(and_(LigandComponent.ligand_id==ligand_id, *expressions))

        query = atom.union(ring)

        return query

    @paginate
    def fetch_all_by_ligand_fragment_id(self, ligand_fragment_id, *expr, **kwargs):
        """
        """
        where = and_(LigandFragmentAtom.ligand_fragment_id==ligand_fragment_id, *expr)

        # ATOM BELONGS TO LIGAND FRAGMENT
        atom = self.query.join((LigandFragmentAtom,
                                LigandFragmentAtom.atom_id==AtomRingInteraction.atom_id)
                               ).filter(where).distinct()

        # RING BELONGS TO LIGAND FRAGMENT
        ring = self.query.join(
            (AromaticRing, AromaticRing.aromatic_ring_id==AtomRingInteraction.aromatic_ring_id),
            (AromaticRingAtom, AromaticRingAtom.aromatic_ring_id==AromaticRing.aromatic_ring_id),
            (LigandComponent, LigandComponent.residue_id==AromaticRing.residue_id),
            (LigandFragment, LigandFragment.ligand_id==LigandComponent.ligand_id),
            (LigandFragmentAtom, and_(LigandFragmentAtom.ligand_fragment_id==LigandFragment.ligand_fragment_id,
                                      LigandFragmentAtom.atom_id==AromaticRingAtom.atom_id))
        ).filter(where).distinct()

        query = atom.union(ring)

        return query


from ..models.hetatm import Hetatm
from ..models.ligandcomponent import LigandComponent
from ..models.ligandfragment import LigandFragment
from ..models.ligandfragmentatom import LigandFragmentAtom
from ..models.aromaticring import AromaticRing
from ..models.aromaticringatom import AromaticRingAtom
from ..models.atomringinteraction import AtomRingInteraction