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

        return bgn.union_all(end).all()

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
        whereclause = and_(Atom.residue_id==residue_id,
                           Atom.biomolecule_id==Contact.biomolecule_id,
                           *expressions)        
        
        bgn = self.query.join('AtomBgn').filter(whereclause)
        end = self.query.join('AtomEnd').filter(whereclause)

        return bgn.union_all(end).all()

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
        whereclause = and_(Ligand.ligand_id==ligand_id, *expressions)       
        
        bgn = self.query.join(
            (Hetatm, Hetatm.atom_id==Contact.atom_bgn_id)
            ).filter(whereclause)

        end = self.query.join(
            (Hetatm, Hetatm.atom_id==Contact.atom_end_id)
            ).filter(whereclause)

        return bgn.union_all(end).all()

    def fetch_all_by_chain_id(self, chain_id, *expressions):
        '''
        '''
        whereclause = and_(Residue.chain_id==chain_id,
                           Residue.biomolecule_id==Atom.biomolecule_id,
                           Atom.biomolecule_id==Contact.biomolecule_id,
                           *expressions)
        
        bgn = self.query.join('AtomBgn','Residue').filter(whereclause)
        end = self.query.join('AtomEnd','Residue').filter(whereclause)

        return bgn.union_all(end).all()

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
        PeptideBgn = aliased(Residue)
        PeptideEnd = aliased(Residue)

        whereclause = and_(Interface.interface_id==interface_id, *expressions)

        query = self.query.join(
            (AtomBgn, and_(AtomBgn.atom_id==Contact.atom_bgn_id, AtomBgn.biomolecule_id==Contact.biomolecule_id)),
            (AtomEnd, and_(AtomEnd.atom_id==Contact.atom_end_id, AtomEnd.biomolecule_id==Contact.biomolecule_id)),
            (PeptideBgn, PeptideBgn.residue_id==AtomBgn.residue_id),
            (PeptideEnd, PeptideEnd.residue_id==AtomEnd.residue_id))
        
        bgn = query.join(Interface, and_(Interface.chain_bgn_id==PeptideBgn.chain_id,
                                         Interface.chain_end_id==PeptideEnd.chain_id))
        bgn = bgn.filter(whereclause)

        end = query.join(Interface, and_(Interface.chain_bgn_id==PeptideEnd.chain_id,
                                         Interface.chain_end_id==PeptideBgn.chain_id))
        end = end.filter(whereclause)

        return bgn.union_all(end).all()

from ..models.hetatm import Hetatm
from ..models.ligandcomponent import LigandComponent
from ..models.residue import Residue
from ..models.contact import Contact
from ..models.atom import Atom
from ..models.interface import Interface