from credoscript import Base
from credoscript.mixins import PathMixin
from credoscript.support.vector import Vector

class AromaticRing(Base, PathMixin):
    """
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
    centroid : str
        The centroid of the aromatic ring (composite type in the database).
    normal : str
        The normal of the aromatic ring (composite type in the database).
    is_hetero_aromatic : bool
        Boolean flag indicating whether this ring contains elements other than
        carbon.

    Mapped Attributes
    -----------------
    Centroid : Vector
    Normal : Vector
    Residue : Residue
        The Residue this ring is part of.
    Atoms : list
        All atoms of this aromatic ring.
    """
    __tablename__ = 'credo.aromatic_rings'

    def __repr__(self):
        """
        """
        return "<AromaticRing({self.path})>".format(self=self)

    @property
    def Centroid(self):
        """
        The centroid of the aromatic ring as Vector object.
        """
        return Vector(self.centroid)

    @property
    def Normal(self):
        """
        The normal of the aromatic ring as Vector object.
        """
        return Vector(self.normal)

    @property
    def Atoms(self):
        """
        """
        return AtomAdaptor().fetch_all_by_aromatic_ring_id(self.aromatic_ring_id,
                                                           self.biomolecule_id,
                                                           dynamic=True)

    @property
    def RingInteractions(self):
        """
        """
        return RingInteractionAdaptor().fetch_all_by_aromatic_ring_id(self.aromatic_ring_id,
                                                                      dynamic=True)

from ..adaptors.atomadaptor import AtomAdaptor
from ..adaptors.ringinteractionadaptor import RingInteractionAdaptor
