from .model import Model
from ..support.vector import Vector

class Atom(Model):
    '''
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

    Notes
    -----

    '''
    def __repr__(self):
        '''
        '''
        return "<Atom({self.atom_name} {self.alt_loc})>".format(self=self)

    @property
    def Contacts(self):
        '''
        '''
        return ContactAdaptor().fetch_all_by_atom_id(self.atom_id)

    @property
    def Coords(self):
        '''
        Returns the coordinates of this atom as Vector object that supports linear
        algebra routines.
        '''
        # POSTGRESQL COMPOSITE TYPE IS RETURNED AS STRING
        centroid = map(float, self.coords[1:-1].split(','))

        return Vector(centroid)

    @property
    def pymolstring(self):
        '''
        Returns a PyMOL selection string in the form
        /PDB//PDB-CHAIN-ID/RESNAME`RESNUMINSCODE/ATOMNAME`ALTLOC.
        Used by the CREDO PyMOL API.

        Returns
        -------
        select : string
            PyMOL selection string.
        '''
        return "{self.Residue.pymolstring}/{self.atom_name}`{self.alt_loc}".format(self=self)

    def get_proximal_water(self, *expressions):
        '''
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
        '''
        return AtomAdaptor().fetch_all_water_by_atom_id(self.atom_id, *expressions)

from ..adaptors.atomadaptor import AtomAdaptor
from ..adaptors.contactadaptor import ContactAdaptor