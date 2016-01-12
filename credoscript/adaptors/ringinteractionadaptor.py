from sqlalchemy.sql.expression import and_, or_

from credoscript.mixins.base import paginate

class RingInteractionAdaptor(object):
    """
    """
    def __init__(self, dynamic=False, paginate=False, per_page=100):
        self.query = RingInteraction.query
        self.dynamic = dynamic
        self.paginate = paginate
        self.per_page = per_page

    def fetch_by_ring_interaction_id(self, ring_interaction_id):
        """
        """
        return self.query.get(ring_interaction_id)

    @paginate
    def fetch_all_by_aromatic_ring_id(self, aromatic_ring_id, *expr, **kwargs):
        """
        """
        query = self.query.filter(and_(or_(RingInteraction.aromatic_ring_bgn_id==aromatic_ring_id,
                                           RingInteraction.aromatic_ring_end_id==aromatic_ring_id),
                                      *expr))

        return query

    @paginate
    def fetch_all_by_ligand_id(self, ligand_id, *expr, **kwargs):
        """
        """
        where = and_(LigandComponent.ligand_id==ligand_id, *expr)

        query = self.query.join(AromaticRing,
                                or_(RingInteraction.aromatic_ring_bgn_id==AromaticRing.aromatic_ring_id,
                                    RingInteraction.aromatic_ring_end_id==AromaticRing.aromatic_ring_id))

        query = query.join(LigandComponent,
                           LigandComponent.residue_id==AromaticRing.residue_id)

        query = query.filter(where)

        return query

    @paginate
    def fetch_all_by_ligand_fragment_id(self, ligand_fragment_id, *expr, **kwargs):
        """
        """
        where = and_(LigandFragmentAtom.ligand_fragment_id==ligand_fragment_id, *expr)

        query = self.query.join(
            (AromaticRing, or_(RingInteraction.aromatic_ring_bgn_id==AromaticRing.aromatic_ring_id,
                               RingInteraction.aromatic_ring_end_id==AromaticRing.aromatic_ring_id)),
            (AromaticRingAtom, AromaticRingAtom.aromatic_ring_id==AromaticRing.aromatic_ring_id),
            (LigandComponent, LigandComponent.residue_id==AromaticRing.residue_id),
            (LigandFragment, LigandFragment.ligand_id==LigandComponent.ligand_id),
            (LigandFragmentAtom, and_(LigandFragmentAtom.ligand_fragment_id==LigandFragment.ligand_fragment_id,
                                      LigandFragmentAtom.atom_id==AromaticRingAtom.atom_id))
        )

        query = query.filter(where)

        return query.distinct()

from ..models.aromaticring import AromaticRing
from ..models.aromaticringatom import AromaticRingAtom
from ..models.ligandcomponent import LigandComponent
from ..models.ligandfragment import LigandFragment
from ..models.ligandfragmentatom import LigandFragmentAtom
from ..models.ringinteraction import RingInteraction
