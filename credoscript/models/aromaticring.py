from sqlalchemy.ext.hybrid import hybrid_property

from credoscript import Base, schema
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
    __tablename__ = '%s.aromatic_rings' % schema['credo']


    def __repr__(self):
        """
        """
        return "<AromaticRing({self.path})>".format(self=self)
    
    def get_imz_string(self, mol_name=None):
        path_toks = self.path.split('/')
        name_concat = '+'.join(at.atom_name for at in self.Atoms)

        s = 0
        if not mol_name:
            s = 2
        elif isinstance(mol_name, basestring):
            path_toks[0] = mol_name
        path_toks[1] = ''
        path = '/'.join(path_toks[s:-1] + [name_concat])

        return "{} ({}) [{}]".format(path,
                                     ' '.join('%.3f' % e for e in self.centroid),
                                     ' '.join('%.3f' % e for e in self.normal))

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
        adaptor = AtomAdaptor(dynamic=True)
        return adaptor.fetch_all_by_aromatic_ring_id(self.aromatic_ring_id,
                                                     self.biomolecule_id)

    @property
    def RingInteractions(self):
        """
        """
        adaptor = RingInteractionAdaptor(dynamic=True)
        return adaptor.fetch_all_by_aromatic_ring_id(self.aromatic_ring_id)

    @hybrid_property
    def is_ligand(self):
        """
        Does the ring belong to a ligand?
        """
        return True if LigandComponentAdaptor().fetch_by_residue_id(self.residue_id) else False


    @is_ligand.expression
    def is_ligand(cls):
        """
        Returns an SQLAlchemy boolean clause list that can enables usage of this property to filter query constructs.
        """
        return LigandComponent.residue_id == cls.residue_id


from ..adaptors.atomadaptor import AtomAdaptor
from ..adaptors.ligandcomponentadaptor import LigandComponentAdaptor, LigandComponent
from ..adaptors.ringinteractionadaptor import RingInteractionAdaptor
