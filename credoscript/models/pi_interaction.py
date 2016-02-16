from sqlalchemy.orm import relationship

from credoscript import Base, schema

class PiInteraction(Base):
    """
    A class that represents a PiInteraction entity from CREDO.

    Attributes
    ----------
    pi_interaction_id : int
        Primary key of.
    pi_bgn_id : int
        Foreign key of the first `PiGroup` or `AromaticRing`.
    pi_bgn_is_ring : bool
        Whether the first pi group is an aromatic ring or not.
    pi_end_id : int
        Foreign key of the second `PiGroup` or `AromaticRing`.
    pi_end_is_ring : bool
        Whether the second pi group is an aromatic ring or not.
    pi_atom_bgn_id : int
        The atom of the first pi group that is the closest to the second.
    pi_atom_end_id : int
        The atom of the second pi group that is the closest to the first.
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
    __tablename__ = '%s.pi_interactions' % schema['credo']

    PiGroupBgn = relationship("PiGroup",
                              primaryjoin="and_(PiGroup.pi_id==PiInteraction.pi_bgn_id, \
                                                PiInteraction.pi_bgn_is_ring==False)",
                              foreign_keys="[PiGroup.pi_id]", uselist=False)

    PiGroupEnd = relationship("PiGroup",
                              primaryjoin="and_(PiGroup.pi_id==PiInteraction.pi_end_id, \
                                                PiInteraction.pi_end_is_ring==False)",
                              foreign_keys="[PiGroup.pi_id]", uselist=False)
    
    AromaticRingBgn = relationship("AromaticRing",
                              primaryjoin="and_(AromaticRing.aromatic_ring_id==PiInteraction.pi_bgn_id, \
                                                PiInteraction.pi_bgn_is_ring==True)",
                              foreign_keys="[AromaticRing.aromatic_ring_id]", uselist=False)

    AromaticRingEnd = relationship("AromaticRing",
                              primaryjoin="and_(AromaticRing.aromatic_ring_id==PiInteraction.pi_end_id, \
                                                PiInteraction.pi_end_is_ring==True)",
                              foreign_keys="[AromaticRing.aromatic_ring_id]", uselist=False)
    
    ClosestAtomBgn = relationship("Atom",
                                  primaryjoin="and_(PiInteraction.closest_atom_bgn_id==Atom.atom_id, PiInteraction.biomolecule_id==Atom.biomolecule_id)",
                                  foreign_keys = "[Atom.atom_id]", uselist=False)

    ClosestAtomEnd = relationship("Atom",
                                  primaryjoin="and_(PiInteraction.closest_atom_end_id==Atom.atom_id, PiInteraction.biomolecule_id==Atom.biomolecule_id)",
                                  foreign_keys = "[Atom.atom_id]", uselist=False)

    def __repr__(self):
        """
        """
        return "<PiInteraction({self.pi_interaction_id} {self.interaction_type})>".format(self=self)

    def get_imz_str(self, mol_name=None):
        '''
        '''

        groups = [g for g in [self.PiGroupBgn, self.AromaticRingBgn, self.PiGroupEnd, self.AromaticRingEnd] if g is not None]
        assert len(groups) == 2, "PiInteraction should only have two group relations, instead: %s" % groups

        fields = [pi.get_imz_string(mol_name) for pi in groups]
        if groups[0].is_ligand and not groups[1].is_ligand:
            fields.reverse()
        fields.append(self.interaction_type or '')

        return '\t'.join(fields)