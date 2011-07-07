from .model import Model
from ..support.vector import Vector

class AromaticRing(Model):
    '''
    An AromaticRing represents the an aromatic ring system of ANY residue in CREDO.

    Attributes
    ----------
    aromatic_ring_id : int
        Primary key.
    residue_id : int
        "Foreign key" of the parent `Residue`.
    biomolecule_id : int
        Foreign key of the parent `Biomolecule`.
    ring_number : int
        The ring number is a sequential number used to assign each atom in the ASU
        to an aromatic ring system .
    size : int
        The number of atoms that are part of this aromatic ring.
    centroid : vector
        The centroid of the aromatic ring (composite type in the database).
    normal : vector
        The normal of the aromatic ring (composite type in the database).
    is_hetero_aromatic : bool
        Boolean flag indicating whether this ring contains elements other than
        carbon.

    Mapped Attributes
    -----------------
    Residue : Residue
        The Residue this ring is part of.
    AromaticRingAtoms : list
        All atoms of this aromatic ring.
    '''
    def __repr__(self):
        '''
        '''
        return "<AromaticRing({self.aromatic_ring_id} {self.size})>".format(self=self)

    def __hash__(self):
        '''
        '''
        return self.aromatic_ring_id

    def __eq__(self, other):
        '''
        '''
        return self.aromatic_ring_id == other.aromatic_ring_id

    def __ne__(self, other):
        '''
        '''
        return self.aromatic_ring_id != other.aromatic_ring_id

    @property
    def Centroid(self):
        '''
        The centroid of the aromatic ring as Vector object.
        '''
        # POSTGRESQL COMPOSITE TYPE IS RETURNED AS STRING
        centroid = map(float, self.centroid[1:-1].split(','))

        return Vector(centroid)

    @property
    def Normal(self):
        '''
        The normal of the aromatic ring as Vector object.
        '''
        # POSTGRESQL COMPOSITE TYPE IS RETURNED AS STRING
        normal = map(float, self.normal[1:-1].split(','))

        return Vector(normal)

    @property
    def pymolstring(self):
        '''
        Returns a PyMOL selection string in the form
        /PDB//PDB-CHAIN-ID/RESNAME`RESNUMINSCODE/CEN[ID].
        Used by the CREDO PyMOL API.

        Returns
        -------
        select : string
            PyMOL selection string.
        '''
        return "{self.Residue.pymolstring}/CX{self.ring_number}".format(self=self)

    def get_ring_interactions(self):
        '''
        '''
        return RingInteractionAdaptor().fetch_all_by_aromatic_ring_id(self.aromatic_ring_id)

from ..adaptors.ringinteractionadaptor import RingInteractionAdaptor