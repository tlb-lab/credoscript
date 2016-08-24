from sqlalchemy.sql.expression import and_, or_

from credoscript.mixins.base import paginate

class PiInteractionAdaptor(object):
    """
    """
    def __init__(self, dynamic=False, paginate=False, per_page=100):
        self.query = PiInteraction.query
        self.dynamic = dynamic
        self.paginate = paginate
        self.per_page = per_page

    def fetch_by_pi_interaction_id(self, pi_interaction_id):
        """
        """
        return self.query.get(pi_interaction_id)

    @paginate
    def fetch_all_by_pi_id(self, pi_id, *expr, **kwargs):
        """
        """
        query = self.query.filter(and_(or_(PiInteraction.pi_bgn_id==pi_id,
                                           PiInteraction.pi_end_id==pi_id),
                                      *expr))

        return query

    @paginate
    def fetch_all_by_ligand_id(self, ligand_id, *expr, **kwargs):
        """
        """
        where = and_(LigandComponent.ligand_id==ligand_id, *expr)

        query = self.query.join(PiGroup,
                                or_(and_(PiInteraction.pi_bgn_id==PiGroup.pi_id, PiInteraction.pi_bgn_is_ring==False),
                                    and_(PiInteraction.pi_end_id==PiGroup.pi_id, PiInteraction.pi_end_is_ring==False)),
                                PiGroup.LigandComponent)

        query = query.filter(where)

        return query

    @paginate
    def fetch_all_by_ligand_fragment_id(self, ligand_fragment_id, *expr, **kwargs):
        """
        """
        where = and_(LigandFragmentAtom.ligand_fragment_id==ligand_fragment_id, *expr)

        query = self.query.join(
            (PiGroup, or_(and_(PiInteraction.pi_bgn_id==PiGroup.pi_id, PiInteraction.pi_bgn_is_ring==False),
                          and_(PiInteraction.pi_end_id==PiGroup.pi_id, PiInteraction.pi_end_is_ring==False))),
            PiGroup.LigandComponent, LigandComponent.LigandFragments, PiGroup.PiGroupAtoms,
            (LigandFragmentAtom, and_(LigandFragmentAtom.ligand_fragment_id==LigandFragment.ligand_fragment_id,
                                      LigandFragmentAtom.atom_id==PiGroupAtom.atom_id))
        )

        query = query.filter(where)

        return query.distinct()

#from ..models.aromaticring import AromaticRing
from ..models.pigroup import PiGroup, PiGroupAtom, PiGroupResidue
from ..models.ligandcomponent import LigandComponent
from ..models.ligandfragment import LigandFragment
from ..models.ligandfragmentatom import LigandFragmentAtom
from ..models.pi_interaction import PiInteraction
