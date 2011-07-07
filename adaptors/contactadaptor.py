from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import and_

from ..meta import session

class ContactAdaptor(object):
    '''
    Class to fetch interatomic contacts from CREDO.
    '''
    def __init__(self):
        '''
        '''
        self.query = session.query(Contact)

    def fetch_by_contact_id(self, contact_id):
        '''
        Parameters
        ----------
        contact_id : int
            Primary key of the `Contact` in CREDO.

        Returns
        -------
        Contact
            CREDO `Contact` object having this contact_id as primary key.

        Examples
        --------
        >>> ContactAdaptor().fetch_by_contact_id(1)
        <Contact(1)>
        '''
        return self.query.get(contact_id)

    def fetch_all_by_atom_id(self, atom_id, *expressions):
        '''
        Returns a list of `Contact` objects that form interatomic contacts with the atom.

        Parameters
        ----------
        atom_id : int
            `Atom` identifier.
        *expressions : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried Entities
        ----------------
        Contact

        Returns
        -------
        contacts : list
            List of `contact` objects.

         Examples
        --------
        >>> ContactAdaptor().fetch_all_by_atom_id(1)
        <Contact()>
        '''
        bgn = self.query.filter(and_(Contact.atom_bgn_id==atom_id, *expressions))
        end = self.query.filter(and_(Contact.atom_end_id==atom_id, *expressions))

        return bgn.union(end).all()

    def fetch_all_by_residue_id(self, residue_id, *expressions):
        '''
        Returns a list of `Contact` objects that form interatomic contacts with the residue.

        Parameters
        ----------
        residue_id : int
            `Residue` identifier.
        *expressions : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried Entities
        ----------------
        Contact, Atom

        Returns
        -------
        contacts : list
            List of `contact` objects.

         Examples
        --------
        >>> ContactAdaptor().fetch_all_by_residue_id(1)
        <Contact()>
        '''
        bgn = self.query.join('AtomBgn').filter(and_(Atom.residue_id==residue_id, *expressions))
        end = self.query.join('AtomEnd').filter(and_(Atom.residue_id==residue_id, *expressions))

        return bgn.union(end).all()

    def fetch_all_by_ligand_id(self, ligand_id, *expressions):
        '''
        Returns a list of `Contact` objects that form interatomic contacts with the atom.

        Parameters
        ----------
        ligand_id : int
            `Ligand` identifier.
        *expressions : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried Entities
        ----------------
        Contact, Hetatm

        Returns
        -------
        contacts : list
            List of `contact` objects.

         Examples
        --------
        >>> ContactAdaptor().fetch_all_by_ligand_id(1)
        <Contact()>
        '''
        bgn = self.query.join(
            (Hetatm, Hetatm.atom_id==Contact.atom_bgn_id)
            ).filter(and_(Hetatm.ligand_id==ligand_id, *expressions))

        end = self.query.join(
            (Hetatm, Hetatm.atom_id==Contact.atom_end_id)
            ).filter(and_(Hetatm.ligand_id==ligand_id, *expressions))

        return bgn.union(end).all()

    def fetch_all_by_interface_id(self, interface_id, *expressions):
        '''
        Returns a list of `Contact` objects that exist in the pairwise interaction
        between two chain in an `Interface`.

        Parameters
        ----------
        interface_id : int
            `Interface` identifier.
        *expressions : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried Entities
        ----------------
        Contact, AtomBgn (Atom), AtomEnd (Atom), ResidueBgn (Residue),
        ResidueEnd (Residue), Interface

        Returns
        -------
        contacts : list
            List of `contact` objects.

         Examples
        --------
        >>> ContactAdaptor().fetch_all_by_interface_id(1)
        <Contact()>
        '''
        AtomBgn = aliased(Atom)
        AtomEnd = aliased(Atom)
        ResidueBgn = aliased(Residue)
        ResidueEnd = aliased(Residue)

        bgn = self.query.join(
            (AtomBgn, AtomBgn.atom_id==Contact.atom_bgn_id),
            (AtomEnd, AtomEnd.atom_id==Contact.atom_end_id),
            (ResidueBgn, ResidueBgn.residue_id==AtomBgn.residue_id),
            (ResidueEnd, ResidueEnd.residue_id==AtomEnd.residue_id),
            (Interface, and_(Interface.chain_bgn_id==ResidueBgn.chain_id,
                             Interface.chain_end_id==ResidueEnd.chain_id))
            ).filter(and_(Interface.interface_id==interface_id,
                          ResidueBgn.is_polymer==True,
                          ResidueEnd.is_polymer==True,
                          *expressions))

        end = self.query.join(
            (AtomBgn, AtomBgn.atom_id==Contact.atom_bgn_id),
            (AtomEnd, AtomEnd.atom_id==Contact.atom_end_id),
            (ResidueBgn, ResidueBgn.residue_id==AtomBgn.residue_id),
            (ResidueEnd, ResidueEnd.residue_id==AtomEnd.residue_id),
            (Interface, and_(Interface.chain_bgn_id==ResidueEnd.chain_id,
                             Interface.chain_end_id==ResidueBgn.chain_id))
            ).filter(and_(Interface.interface_id==interface_id,
                          ResidueBgn.is_polymer==True,
                          ResidueEnd.is_polymer==True,
                          *expressions))

        return bgn.union(end).all()

from ..models.hetatm import Hetatm
from ..models.ligandcomponent import LigandComponent
from ..models.residue import Residue
from ..models.contact import Contact
from ..models.atom import Atom
from ..models.interface import Interface