from itertools import groupby

from sqlalchemy.orm import backref, relationship, column_property
from sqlalchemy.sql.expression import and_, func, or_
from sqlalchemy.ext.hybrid import hybrid_property

from credoscript import Base, BaseQuery, schema, pi_groups, pi_residues
from credoscript.mixins import PathMixin
from credoscript.support.vector import Vector

class PiGroup(Base): #, PathMixin):
    """
    An PiGroup represents the an non-ring Pi-group system of ANY residue in CREDO.

    Attributes
    ----------
    pi_id : int
        Primary key.
    residue_ids : int_array
        "Foreign key" of the parent `Residues`.
    biomolecule_id : int
        Foreign key of the parent `Biomolecule`.
    pi_serial : int
        The pi serial is a sequential number used to assign each atom in the ASU
        to an pi group system .
    size : int
        The number of atoms that are part of this pi group.
    centroid : str
        The centroid of the aromatic ring (composite type in the database).
    normal : str
        The normal of the aromatic ring (composite type in the database).


    Mapped Attributes
    -----------------
    Centroid : Vector
    Normal : Vector
    Residues : list
        The Residues this pi group consists of.
    Atoms : list
        All atoms of this pi group.
    """
    __table__ = pi_groups.join(pi_residues, onclause=pi_groups.c.pi_id == pi_residues.c.pi_id)
    #__tablename__ = '%s.pi_groups' % schema['credo']

    pi_id = column_property(pi_groups.c.pi_id, pi_residues.c.pi_id)
    biomolecule_id = column_property(pi_groups.c.biomolecule_id, pi_residues.c.biomolecule_id)

    Residues = relationship("Residue", query_class=BaseQuery,
                             primaryjoin="and_(PiGroup.residue_id==Residue.residue_id, " +
                                              "PiGroup.biomolecule_id==Residue.biomolecule_id)",
                             foreign_keys="[Residue.residue_id, Residue.biomolecule_id]",
                             uselist=True, innerjoin=True, lazy='dynamic')


    LigandComponent = relationship("LigandComponent",  query_class=BaseQuery,
                             primaryjoin="PiGroup.residue_id==LigandComponent.residue_id",
                             foreign_keys="[LigandComponent.residue_id]",
                             uselist=True, innerjoin=True, lazy='dynamic')


    def __repr__(self):
        """
        """
        return "<PiGroup({self.path})>".format(self=self)

    def get_imz_string(self, mol_name=None):
        res = []
        for res_info, res_atoms in groupby(self.Atoms, key=lambda a: (a.chain_id, a.res_name, a.res_num, a.ins_code)):
            if mol_name is True:
                res_atoms = [a for a in res_atoms]
                res_path = res_atoms[0].Residue.pymolstring
            elif not mol_name:
                res_path = '{}/{}`{}{}'.format(res_info[0].strip() or '""', res_info[1], res_info[2], res_info[3].strip())
            else:
                res_path = '/{}//{}/{}`{}{}'.format(mol_name, res_info[0].strip() or '""',
                                                   res_info[1], res_info[2], res_info[3].strip())

            res.append("%s/%s" % (res_path, '+'.join(a.atom_name for a in res_atoms)))
        return ' '.join(res)

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
        return adaptor.fetch_all_by_pi_id(self.pi_id, self.biomolecule_id)

    @property
    def PiGroupInteractions(self):
        """
        """
        adaptor = PiInteractionAdaptor(dynamic=True)
        return adaptor.fetch_all_by_pi_id(self.pi_id)

    @hybrid_property
    def is_ligand(self):
        """
        Does the ring belong to a ligand?
        """
        if any(LigandComponentAdaptor().fetch_by_residue_id(r.residue_id) for r in self.Residues):
            return True
        else:
            return False

    @is_ligand.expression
    def is_ligand(cls):
        """
        Returns an SQLAlchemy boolean clause list that can enables usage of this property to filter query constructs.
        """
        return LigandComponent.residue_id == cls.residue_id

from ..adaptors.atomadaptor import AtomAdaptor
from ..adaptors.pi_interactionadaptor import PiInteractionAdaptor
from ..adaptors.ligandcomponentadaptor import LigandComponentAdaptor, LigandComponent
