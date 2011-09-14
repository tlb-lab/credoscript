from sqlalchemy.dialects.postgresql import INTEGER
from sqlalchemy.sql.expression import and_, cast, func

from ..meta import session
from .model import Model

class Residue(Model):
    '''
    Represents a PDB Residue of ANY type.

    Attributes
    ----------
    residue_id : int
        Primary key.
    chain_id : int
        "Foreign key" of the parent `Chain`.
    res_name : str
        The PDB three-letter chemical component name / Three-letter amino acid code.
    one_letter_code : string
        The one-letter code of this amino acid.
    res_num : int
        The PDB residue number.
    ins_code : str
        The PDB insertion code.
    entity_type_bm : int
        Entity type bitmask containing six bits.

    Mapped attributes
    -----------------
    Atoms : list
        A list of `Atom` objects.
    Rings : list
        A list of `AromaticRing` objects in case of aromatic residues.
    XRefs : list
        A list of CREDO `XRef` objects.

    Notes
    -----
    The __getitem__ method is overloaded to allow accessing Atoms directly by
    their names, e.g. Residue['CA']. Returns a list due to atoms with
    possible alternate locations.
    '''
    def __repr__(self):
        '''
        '''
        return "<Residue({self.res_name} {self.res_num}{self.ins_code})>".format(self=self)

    def __getitem__(self, atom):
        '''
        '''
        # ONLY ATOM NAME IS PROVIDED / WILL TREAT ALTERNATE LOCATION AS BLANK
        if isinstance(atom, str): return self.Atoms.get((atom, ' '))

        # ALTERNATE LOCATION WAS PROVIDED AS WELL
        elif isinstance(atom, tuple): return self.Atoms.get(atom)

    def __iter__(self):
        '''
        '''
        return iter(self.Atoms.values())

    @property
    def pymolstring(self):
        '''
        Returns a PyMOL selection string in the form /PDB//PDB-CHAIN-ID/RESNAME`RESNUMINSCODE.
        Used by the CREDO PyMOL API.

        Returns
        -------
        select : string
            PyMOL selection string.
        '''
        return "/{0}-{1}//{2}/{3}`{4}".format(self.Chain.Biomolecule.Structure.pdb,
                                              self.Chain.Biomolecule.assembly_serial,
                                              self.Chain.pdb_chain_id, self.res_name,
                                              str(self.res_num)+self.ins_code.strip())

    def get_contacts(self, *expressions):
        '''
        '''
        return ContactAdaptor().fetch_all_by_residue_id(self.residue_id, *expressions)

    def get_proximal_water(self, *expressions):
        '''
        Returns all water atoms that are in contact with this residue.

        Parameters
        ----------
        *expressions : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried entities
        ----------------
        Subquery (not exposed), Atom

        Returns
        -------
        atoms : list
            List of `Atom` objects.

        Examples
        --------
        >>>
        '''
        return AtomAdaptor().fetch_all_water_by_residue_id(self.residue_id, *expressions)

    def get_sift(self, *expressions):
        '''
        Returns the sum of all the contact types of all the contacts this residue
        has as a tuple. 
        
        Queried entities
        ----------------
        Residue, Atom, Contact
        
        Returns
        -------
        sift : tuple
            sum of all the contact types of all contacts this residue has.
        '''
        whereclause = and_(Atom.residue_id==self.residue_id, *expressions)

        bgn = session.query(Contact).join(Atom, Contact.atom_bgn_id==Atom.atom_id).filter(whereclause)
        end = session.query(Contact).join(Atom, Contact.atom_end_id==Atom.atom_id).filter(whereclause)
        
        subquery = bgn.union(end).subquery(name='contacts')
                
        sift = (func.sum(cast(subquery.c.credo_contacts_is_covalent, INTEGER)),
                func.sum(cast(subquery.c.credo_contacts_is_vdw_clash, INTEGER)),
                func.sum(cast(subquery.c.credo_contacts_is_vdw, INTEGER)),
                func.sum(cast(subquery.c.credo_contacts_is_proximal, INTEGER)),
                func.sum(cast(subquery.c.credo_contacts_is_hbond, INTEGER)),
                func.sum(cast(subquery.c.credo_contacts_is_weak_hbond, INTEGER)),
                func.sum(cast(subquery.c.credo_contacts_is_xbond, INTEGER)),
                func.sum(cast(subquery.c.credo_contacts_is_ionic, INTEGER)),
                func.sum(cast(subquery.c.credo_contacts_is_metal_complex, INTEGER)),
                func.sum(cast(subquery.c.credo_contacts_is_aromatic, INTEGER)),
                func.sum(cast(subquery.c.credo_contacts_is_hydrophobic, INTEGER)),
                func.sum(cast(subquery.c.credo_contacts_is_carbonyl, INTEGER)))
        
        query = session.query(*sift)

        return query.first()

from .contact import Contact
from .atom import Atom
from ..adaptors.atomadaptor import AtomAdaptor
from ..adaptors.contactadaptor import ContactAdaptor
from ..adaptors.protfragmentadaptor import ProtFragmentAdaptor