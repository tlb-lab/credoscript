from sqlalchemy.orm import relationship

from credoscript import Base, schema

class RingInteraction(Base):
    """
    A class that represents a RingInteraction entity from CREDO.

    Attributes
    ----------
    ring_interaction_id : int
        Primary key of.
    aromatic_ring_bgn_id : int
        Foreign key of the first `AromaticRing`.
    aromatic_ring_end_id : int
        Foreign key of the second `AromaticRing`.
    closest_atom_bgn_id : int
        The atom of the first aromatic ring that is the closest to the second.
    closest_atom_end_id : int
        The atom of the second aromatic ring that is the closest to the first.
    distance : float
        Distance between the centroids of the aromatic rings.
    closest_atom_distance : float
        Distance between the closest aromatic atoms of the two rings.
    dihedral : float
        Dihedral angle between the planes of the aromatic rings.
    theta : float
    iota : float
    interaction_type : str
        - FF
        - OF
        - EE
        - FT
        - OT
        - ET
        - FE
        - OE
        - EF


    Mapped Attributes
    -----------------

    Notes
    -----
    """
    __tablename__ = '%s.ring_interactions' % schema['credo']

    AromaticRingBgn = relationship("AromaticRing",
                                     primaryjoin="AromaticRing.aromatic_ring_id==RingInteraction.aromatic_ring_bgn_id",
                                     foreign_keys="[AromaticRing.aromatic_ring_id]",
                                     uselist=False, innerjoin=True)

    AromaticRingEnd = relationship("AromaticRing",
                                     primaryjoin="AromaticRing.aromatic_ring_id==RingInteraction.aromatic_ring_end_id",
                                     foreign_keys="[AromaticRing.aromatic_ring_id]",
                                     uselist=False, innerjoin=True)

    ClosestAtomBgn = relationship("Atom",
                                    primaryjoin="and_(RingInteraction.closest_atom_bgn_id==Atom.atom_id, RingInteraction.biomolecule_id==Atom.biomolecule_id)",
                                    foreign_keys = "[Atom.atom_id]",
                                    uselist=False, innerjoin=True)

    ClosestAtomEnd = relationship("Atom",
                                    primaryjoin="and_(RingInteraction.closest_atom_end_id==Atom.atom_id, RingInteraction.biomolecule_id==Atom.biomolecule_id)",
                                    foreign_keys = "[Atom.atom_id]",
                                    uselist=False, innerjoin=True)

    def __repr__(self):
        """
        """
        return "<RingInteraction({self.ring_interaction_id} {self.interaction_type})>".format(self=self)

    def get_imz_str(self, mol_name=None):
        '''
        '''
        fields = [ring.get_imz_string(mol_name) for ring in (self.AromaticRingBgn, self.AromaticRingEnd)]

        if self.AromaticRingBgn.is_ligand and not self.AromaticRingEnd.is_ligand:
            fields.reverse()
        fields.append(self.interaction_type)

        return '\t'.join(fields)
