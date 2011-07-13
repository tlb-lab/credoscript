from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import and_

from ..meta import session, binding_sites, ligand_fragment_atoms

class ResidueAdaptor(object):
    '''
    '''
    def __init__(self):
        '''
        '''
        self.query = session.query(Residue)

    def fetch_by_residue_id(self, residue_id):
        '''
        Parameters
        ----------
        residue_id : int
            Primary key of the `Residue` in CREDO.

        Returns
        -------
        Atom
            CREDO `Residue` object having this atom_id as primary key.

        Examples
        --------
        >>> ResidueAdaptor().fetch_by_residue_id(1)
        <Residue(1)>
        '''
        return self.query.get(residue_id)

    def fetch_all_by_ligand_id(self, ligand_id, *expressions):
        '''
        Returns a list of `Residues` that are part of the ligand with the given identifier.

        Parameters
        ----------
        ligand_id : int
            `Ligand` identifier.
        *expressions : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried Entities
        ----------------
        Residue, LigandComponent

        Returns
        -------
        contacts : list
            List of `Residue` objects.

         Examples
        --------
        >>> ResidueAdaptor().fetch_all_by_ligand_id(4343)
        [<Atom(C01  )>, <Atom(C02  )>, <Atom(N03  )>, <Atom(C04  )>, <Atom(O05  )>,...]
        '''
        query = self.query.join(
            (LigandComponent, LigandComponent.residue_id==Residue.residue_id)
            ).filter(and_(LigandComponent.ligand_id==ligand_id, *expressions))

        return query.all()

    def fetch_all_by_biomolecule_id(self, biomolecule_id, *expressions):
        '''
        Returns the `Residue` objects of a `Biomolecule`.

        Parameters
        ----------
        biomolecule_id : int
            `Biomolecule` identifier.
        *expressions : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried Entities
        ----------------
        Residue, Chain

        Returns
        -------
        contacts : list
            List of `Residue` objects.

         Examples
        --------
        >>> ResidueAdaptor().fetch_all_by_biomolecule_id(4343)

        '''
        query = self.query.join('Chain').filter(and_(Chain.biomolecule_id==biomolecule_id, *expressions))

        return query.all()

    def fetch_all_in_contact_with_residue_id(self, residue_id, *expressions):
        '''
        Returns all the Residues that are in contact with the Residue having the
        specified residue_id.
        
        Parameters
        ----------
        residue_id : int
            Primary key of the Residue.
        *expressions : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.
        
        Returns
        -------
        residues : list
            Residues that are in contact with the Residue having the specified
            residue_id.
        
        Queried Entities
        ----------------
        Residue, Atom, Contact
        
        Examples
        --------
        >>>> ResidueAdaptor().fetch_all_in_contact_with_residue_id(271510, Contact.interaction_type_id==PRO_PRO)
        [<Residue(ILE 160 )>, <Residue(TYR 159 )>, <Residue(ALA 192 )>,
         <Residue(MSE 158 )>, <Residue(TYR 191 )>, <Residue(ALA 207 )>,
         <Residue(VAL 1532 )>, <Residue(GLN 206 )>, <Residue(ALA 190 )>,
         <Residue(MSE 210 )>, <Residue(LEU 203 )>]
        '''
        Other = aliased(Atom)
        query = self.query.join('Atoms')
        
        bgn = query.join((Contact, Contact.atom_bgn_id==Atom.atom_id),
                         (Other, Other.atom_id==Contact.atom_end_id)
                         ).filter(and_(Other.residue_id==residue_id, *expressions))
        
        end = query.join((Contact, Contact.atom_end_id==Atom.atom_id),
                         (Other, Other.atom_id==Contact.atom_bgn_id)
                         ).filter(and_(Other.residue_id==residue_id, *expressions))

        return bgn.union(end).all()

    def fetch_all_in_contact_with_ligand_id(self, ligand_id, *expressions):
        '''
        Returns all residues that are in contact with the ligand having the specified
        ligand identifier.

        Parameters
        ----------
        ligand_id : int
            `Ligand` identifier.
        *expressions : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried Entities
        ----------------
        Residue, binding_sites

        Returns
        -------
        residues : list
            List of `Residue` objects.
        '''
        return self.query.join(
            (binding_sites, binding_sites.c.residue_id==Residue.residue_id)
            ).filter(and_(binding_sites.c.ligand_id==ligand_id, *expressions)).all()

    def fetch_all_in_contact_with_ligand_fragment_id(self, ligand_fragment_id, *expressions):
        '''
        Returns all residues that are in contact with the ligand fragment having the specified
        identifier.

        Parameters
        ----------
        ligand_fragment_id : int
            `LigandFragment` identifier.
        *expressions : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried Entities
        ----------------
        Residue, Atom, Contact, ligand_fragment_atoms

        Returns
        -------
        residues : list
            List of `Residue` objects.
        '''
        bgn = self.query.join(
            (Atom, Atom.residue_id==Residue.residue_id),
            (Contact, Contact.atom_bgn_id==Atom.atom_id),
            (ligand_fragment_atoms, ligand_fragment_atoms.c.atom_id==Contact.atom_end_id)
            ).filter(and_(ligand_fragment_atoms.c.ligand_fragment_id==ligand_fragment_id, *expressions))

        end = self.query.join(
            (Atom, Atom.residue_id==Residue.residue_id),
            (Contact, Contact.atom_end_id==Atom.atom_id),
            (ligand_fragment_atoms, ligand_fragment_atoms.c.atom_id==Contact.atom_bgn_id)
            ).filter(and_(ligand_fragment_atoms.c.ligand_fragment_id==ligand_fragment_id, *expressions))

        return bgn.union(end).all()

from ..models.contact import Contact
from ..models.atom import Atom
from ..models.residue import Residue
from ..models.chain import Chain
from ..models.ligandcomponent import LigandComponent