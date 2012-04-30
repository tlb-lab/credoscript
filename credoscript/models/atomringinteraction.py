from sqlalchemy.orm import backref, relationship

from credoscript import Base

class AtomRingInteraction(Base):
    '''
    '''
    __tablename__ = 'credo.atom_ring_interactions'

    Atom = relationship("Atom",
                        primaryjoin="Atom.atom_id==AtomRingInteraction.atom_id",
                        foreign_keys="[Atom.atom_id]", uselist=False, innerjoin=True)

    AromaticRing = relationship("AromaticRing",
                                primaryjoin="AromaticRing.aromatic_ring_id==AtomRingInteraction.aromatic_ring_id",
                                foreign_keys="[AromaticRing.aromatic_ring_id]",
                                uselist=False, innerjoin=True,
                                backref=backref('AtomRingInteractions',
                                                uselist=True, innerjoin=True, lazy='dynamic'))

    def __repr__(self):
        '''
        '''
        return '<AtomRingInteraction({self.atom_ring_interaction_id})>'.format(self=self)