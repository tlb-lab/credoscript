from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql.expression import or_
from sqlalchemy.ext.hybrid import hybrid_method

from credoscript import Base, BaseQuery, schema
from credoscript.mixins import PathMixin
from credoscript.support.vector import Vector

class Atom(Base, PathMixin):
    """
    Represents an Atom entity from CREDO.

    Attributes
    ----------
    atom_id : int
        Primary key.
    residue_id : int
        Foreign key of the parent `Residue`.
    biomolecule_id : int
        Foreign key of the parent `Biomolecule`.
    group_pdb : string
        'ATOM' or 'HETATM'.
    atom_serial : int
        The PDB serial number.
    atom_name : string
        PDB atom name.
    alt_loc : string
        The alternate location code.
    coords : vector
    occupancy : float
    b_factor : float
    element : string
    hyb : int
        OpenEye atom hybridisation namespace.
    tripos_atom_type : string
        Tripos atom type.
    is_donor : bool

    is_acceptor : bool

    is_aromatic : bool

    is_weak_acceptor : bool

    is_weak_donor : bool

    is_hydrophobe : bool

    is_metal : bool

    is_pos_ionisable : bool

    is_neg_ionisable : bool

    is_xbond_donor : bool

    is_xbond_acceptor : bool

    is_carbonyl_oxygen : bool

    is_carbonyl_carbon : bool

    Mapped attributes
    -----------------
    Coords : Vector
    Contacts : Query
        Contacts that this Atom forms with other Atoms.

    Notes
    -----

    """
    __tablename__ = '%s.atoms' % schema['credo']

    Contacts  = relationship("Contact", query_class=BaseQuery,
                             primaryjoin="and_(or_(Contact.atom_bgn_id==Atom.atom_id, Contact.atom_end_id==Atom.atom_id), Contact.biomolecule_id==Atom.biomolecule_id)",
                             foreign_keys="[Contact.atom_bgn_id, Contact.atom_end_id, Contact.biomolecule_id]",
                             uselist=True, innerjoin=True, lazy='dynamic',
                             backref=backref('Atoms', uselist=True, innerjoin=True))

    def __repr__(self):
        """
        """
        return "<Atom({self.path})>".format(self=self)
        
    @property
    def res_num(self):
        return self.Residue.res_num
        
    @property
    def res_name(self):
        return self.Residue.res_name
        
    @property
    def ins_code(self):
        return self.Residue.ins_code
        
    @property
    def chain_id(self):
        return self.Residue.Chain.pdb_chain_id

    @property
    def _atom_name_alt_loc_tuple(self):
        """
        Full name of a PDB atom consisting of its name and alternate location identifier.
        Only used for the Residue|Peptide.Atom mappers.
        """
        return self.atom_name, self.alt_loc

    @property
    def pdb_line(self):
        name_fix = " %s" % self.atom_name if (len(self.atom_name) < 4 and not self.atom_name.startswith('H')) else self.atom_name
        line = "{:6s}{:5d} {:4s}{:1s}{:3s} {:1s}{:4d}{:1s}   {:8.3f}{:8.3f}{:8.3f}{:6.2f}{:6.2f}          {:>2s}  \n".format(
               self.group_pdb, self.atom_serial, name_fix, self.alt_loc, self.res_name,
               self.chain_id, self.res_num, self.ins_code, self.coords[0], self.coords[1], self.coords[2],
               self.occupancy, self.b_factor, self.element)
        return line
    
    @property
    def Vector(self):
        """
        Returns the coordinates of this atom as Vector object that supports linear
        algebra routines.
        """
        return Vector(self.coords)

    @property
    def ProximalWater(self):
        """
        Returns all water atoms that are in contact with this atom.

        Parameters
        ----------
        *expressions : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Joins
        -----
        Subquery (not exposed)

        Returns
        -------
        atoms : list
            List of `Atom` objects.

         Examples
        --------
        >>>
        """
        adaptor = AtomAdaptor(dynamic=True)
        return adaptor.fetch_all_water_in_contact_with_atom_id(self.atom_id,
                                                               self.biomolecule_id)

    @hybrid_method
    @property
    def is_polar(self):
        """
        Meta atom type indicating whether the atom is polar or not. The traditional
        medinical chemistry definition for polar atoms is used, i.e. either oxygen
        or nitrogen.
        """
        return any((self.element=='O', self.element=='N'))

    @is_polar.expression
    @property
    def is_polar(self):
        """
        Returns an SQLAlchemy boolean clause list that can enables usage of this
        meta atom type to filter query constructs.
        """
        return or_(Atom.element=='O', Atom.element=='N')

    @hybrid_method
    @property
    def is_mc(self):
        """
        Meta atom type indicating if the atom belongs to a protein backbone or
        not.
        """
        return any((self.atom_name=='C', self.atom_name=='N',
                    self.atom_name=='CA', self.atom_name=='O'))

    @is_mc.expression
    @property
    def is_mc(self):
        """
        """
        return or_(Atom.atom_name=='C', Atom.atom_name=='N',
                   Atom.atom_name=='CA', Atom.atom_name=='O')
    
    @property
    def type_bm(self):
        all_prop = ["is_acceptor","is_donor","is_weak_acceptor","is_weak_donor","is_xbond_acceptor","is_xbond_donor",
                    "is_pos_ionisable" ,"is_neg_ionisable","is_aromatic","is_hydrophobe",
                    "is_carbonyl_carbon","is_carbonyl_oxygen","is_metal"]

        return sum([int(getattr(self, prop, 0)) << i for (i, prop) in enumerate(all_prop)])
        

from ..adaptors.atomadaptor import AtomAdaptor
