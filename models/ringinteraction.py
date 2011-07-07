from .model import Model

class RingInteraction(Model):
    '''
    A class that represents a RingInteraction entity from CREDO.

    Attributes
    ----------
    ring_interaction_id : int
        Primary key of.
    aromatic_ring_bgn_id : int
        Foreign key of the first `AromaticRing`.
    aromatic_ring_end_id : int
        Foreign key of the second `AromaticRing`.
    aromatic_ring_atom_bgn_id : int
        The atom of the first aromatic ring that is the closest to the second.
    aromatic_ring_atom_end_id : int
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
    '''
    def __repr__(self):
        '''
        '''
        return "<RingInteraction({self.ring_interaction_id} {self.interaction_type})>".format(self=self)

    def __hash__(self):
        '''
        '''
        return self.ring_interaction_id

    def __eq__(self, other):
        '''
        '''
        return self.ring_interaction_id == other.ring_interaction_id

    def __ne__(self, other):
        '''
        '''
        return self.ring_interaction_id != other.ring_interaction_id