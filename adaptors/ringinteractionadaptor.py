from sqlalchemy.sql.expression import and_, or_

from credoscript import session

class RingInteractionAdaptor(object):
    '''
    '''
    def __init__(self):
        '''
        '''
        self.query = self.session.query(RingInteraction)

    def fetch_by_ring_interaction_id(self, ring_interaction_id):
        '''
        '''
        return self.query.get(ring_interaction_id)

    def fetch_all_by_aromatic_ring_id(self, aromatic_ring_id, *expressions):
        '''
        '''
        return self.query.filter(and_(or_(RingInteraction.aromatic_ring_bgn_id==aromatic_ring_id,
                                          RingInteraction.aromatic_ring_end_id==aromatic_ring_id),
                                      *expressions)).all()

    def fetch_all_by_ligand_id(self, ligand_id, *expressions):
        '''
        '''
        bgn = self.query.join(
            (AromaticRing, AromaticRing.aromatic_ring_id==RingInteraction.aromatic_ring_bgn_id),
            (LigandComponent, LigandComponent.residue_id==AromaticRing.residue_id)
            ).filter(and_(LigandComponent.ligand_id==ligand_id, *expressions))

        end = self.query.join(
            (AromaticRing, AromaticRing.aromatic_ring_id==RingInteraction.aromatic_ring_end_id),
            (LigandComponent, LigandComponent.residue_id==AromaticRing.residue_id)
            ).filter(and_(LigandComponent.ligand_id==ligand_id, *expressions))

        return bgn.union(end).all()

from ..models.residue import Residue
from ..models.aromaticring import AromaticRing
from ..models.ligandcomponent import LigandComponent
from ..models.ringinteraction import RingInteraction