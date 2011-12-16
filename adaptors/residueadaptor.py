from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import and_

from credoscript import session, binding_sites, interface_residues

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
        Residue
            CREDO `Residue` object having this atom_id as primary key.

        Examples
        --------
        >>> ResidueAdaptor().fetch_by_residue_id(1)
        <Residue(1)>
        '''
        return self.query.get(residue_id)

    def fetch_all_by_chain_id(self, chain_id, *expressions):
        '''
        Returns all residues that are part of the chain with the specified chain_id.
        
        Parameters
        ----------
        chain_id : int
            CREDO chain_id.
        *expressions : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried Entities
        ----------------
        Residue

        Returns
        -------
        residues : list
            residues that are part of the chain with the specified chain_id.

        Examples
        --------

        '''
        return self.query.filter(and_(Residue.chain_id==chain_id,*expressions)).all()

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
        query = self.query.filter(and_(Residue.biomolecule_id==biomolecule_id, *expressions))

        return query.all()

    def fetch_all_by_interface_id(self, interface_id, *expressions):
        '''
        Returns all the residues (including solvents) that are interacting across
        the interface.

        Parameters
        ----------
        interface_id : int
            Primary key of the interface.
        *expressions : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried Entities
        ----------------
        Residue, interface_residues

        Returns
        -------
        contacts : list
            List of residues.

         Examples
        --------
        >>> interface = InterfaceAdaptor().fetch_by_interface_id(128)
        >>> interface.get_residues(Residue.entity_type_bm==32)
        >>> [<Residue(VAL 32 )>, <Residue(THR 91 )>, <Residue(LEU 23 )>,
             <Residue(ASP 30 )>, <Residue(GLY 49 )>, <Residue(ARG 87 )>,...]
        '''
        whereclause = and_(interface_residues.c.interface_id==interface_id, *expressions)
        
        bgn = self.query.join(interface_residues, interface_residues.c.residue_bgn_id==Residue.residue_id).filter(whereclause)
        end = self.query.join(interface_residues, interface_residues.c.residue_end_id==Residue.residue_id).filter(whereclause)
        
        query = bgn.union(end)
        
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
        
        whereclause = and_(Other.residue_id==residue_id,
                           Atom.biomolecule_id==Contact.biomolecule_id,
                           *expressions)
        
        bgn = query.join((Contact, Contact.atom_bgn_id==Atom.atom_id),
                         (Other, Other.atom_id==Contact.atom_end_id)
                         ).filter(whereclause)
        
        end = query.join((Contact, Contact.atom_end_id==Atom.atom_id),
                         (Other, Other.atom_id==Contact.atom_bgn_id)
                         ).filter(whereclause)

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
            (ligand_fragment_atoms, LigandFragmentAtom.atom_id==Contact.atom_end_id)
            ).filter(and_(LigandFragmentAtom.ligand_fragment_id==ligand_fragment_id, *expressions))

        end = self.query.join(
            (Atom, Atom.residue_id==Residue.residue_id),
            (Contact, Contact.atom_end_id==Atom.atom_id),
            (ligand_fragment_atoms, LigandFragmentAtom.atom_id==Contact.atom_bgn_id)
            ).filter(and_(LigandFragmentAtom.ligand_fragment_id==ligand_fragment_id, *expressions))

        return bgn.union(end).all()

from ..models.contact import Contact
from ..models.atom import Atom
from ..models.residue import Residue
from ..models.chain import Chain
from ..models.ligandcomponent import LigandComponent
from ..models.ligandfragmentatom import LigandFragmentAtom