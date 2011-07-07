from sqlalchemy.sql.expression import and_, func

from .model import Model
from ..meta import session, ligand_usr, ligand_molstrings

class Ligand(Model):
    '''
    Represents a `Ligand` entity from CREDO. A `Ligand` object in CREDO can consist
    of more than one chemical component (maximum 10).

    Attributes
    ----------
    ligand_id : int
        Primary key of this object.
    structure_id : int
        "Foreign key" of the parent `Structure` (Structure.id).
    ligand_name : string
        String consisting of the concatenated chemical component names (HET ID)
        of all `LigandComponent` objects.
    pdb_chain_id : string
        PDB chain identifier of this Ligand.
    res_num : int or None
        PDB residue number. None in case of a `Ligand` with more than one
        `LigandComponent`.
    num_hvy_atoms : int
        Number of all observed heavy atoms of this Ligand.
    ism : string
        Canonical isomeric SMILES string of this Ligand. Very useful in cases of
        ligands consisting of more than one chemical component.
    is_incomplete : bool
        Boolean flag indicating whether this Ligand has missing (not observed)
        atoms.
    is_substrate : bool
        Boolean flag whether this Ligand is annotated as a substrate in a reaction
        involving the EC code of the chain its in contact with.
    is_product : bool
        Boolean flag whether this Ligand is annotated as a product in a reaction
        involving the EC code of the chain its in contact with.
    is_cofactor : bool
        Boolean flag whether this Ligand is annotated as a cofactor in a reaction
        involving the EC code of the chain its in contact with.
    is_solvent : bool
        Boolean flag indicating whether this ligand is part of the Astex solvents
        list.
    is_promiscuous : bool
    is_drug_target_int : bool

    Mapped Attributes
    -----------------
    Components : list
        A list of `LigandComponent` objects.
    Residues : list
        The Residues this ligand consists of.
    LigandFragments : list

    Atoms : list
        A list of `Atom` objects, i.e. the atoms this Ligand consists of.
    AromaticRings : list
        A list of `LigandRing` objects, mapped as association_proxy via LigandComponents.

    Overloaded operators
    --------------------
    __or__
        Returns the USR similarity between this and another Ligand
        (Overloads | operator).

    See Also
    --------
    LigandAdaptor : Fetch Ligands from the database.
    '''
    def __repr__(self):
        '''
        '''
        return '<Ligand({self.pdb_chain_id} {self.res_num} {self.name})>'.format(self=self)

    def __len__(self):
        '''
        '''
        return self.num_hvy_atoms

    def __iter__(self):
        '''
        '''
        return iter(self.Components)

    def __or__(self, other):
        '''
        Returns the USR similarity between this and another Ligand. Overloads '|'
        operator.

        Returns
        -------
        usr : float
            The USR similarity between two ligands.
        '''
        if isinstance(other, Ligand):
            distance = sum([abs(a - b) for a, b in zip(self.usr_space, other.usr_space)])
            return 1.0 / (1.0 + distance / 12.0)

    @property
    def Residues(self):
        '''
        Returns all the Residues this Ligand consists of.

        Returns
        -------
        residues : list
            All the Residues of this Ligand.
        '''
        return ResidueAdaptor().fetch_all_by_ligand_id(self.ligand_id)

    @property
    def AromaticRings(self):
        '''
        Returns all AromaticRing entities found in this Ligand (if any).

        Returns
        -------
        aromatic_rings : list
            All the AromaticRings of this Ligand.
        '''
        return AromaticRingAdaptor().fetch_all_by_ligand_id(self.ligand_id)

    @property
    def Atoms(self):
        '''
        Returns all Atoms of this Ligand.

        Returns
        -------
        atoms : list
            All the Atoms of this Ligand.
        '''
        return AtomAdaptor().fetch_all_by_ligand_id(self.ligand_id)

    @property
    def ism(self):
        '''
        Isomeric SMILES string of this Ligand (taken straight from the PDB structure).

        Returns
        -------
        ism : str
            Isomeric SMILES string of this Ligand.
        '''
        query = session.query(ligand_molstrings.c.ism)
        query = query.filter(ligand_molstrings.c.ligand_id==self.ligand_id)

        return query.scalar()

    @property
    def usr_space(self):
        '''
        '''
        return session.query(ligand_usr.c.usr_space).filter(
            ligand_usr.c.ligand_id==self.ligand_id).scalar()

    @property
    def usr_moments(self):
        '''
        '''
        return session.query(ligand_usr.c.usr_moments).filter(
            ligand_usr.c.ligand_id==self.ligand_id).scalar()

    @property
    def pymolstring(self):
        '''
        Returns a PyMOL select string in the form /PDB//PDB-CHAIN-ID/RESNUM.
        Used by the CREDO PyMOL API.

        Returns
        -------
        select : string
            PyMOL selection string.
        '''
        return "/{0}-{1}//{2}/{3}".format(self.Biomolecule.Structure.pdb,
                                          self.Biomolecule.biomolecule,
                                          self.pdb_chain_id,
                                          self.res_num and self.res_num or '')

    def get_contacts(self, *expressions):
        '''
        '''
        return ContactAdaptor().fetch_all_by_ligand_id(self.ligand_id, *expressions)

    def get_xrefs(self, *expressions):
        '''
        '''
        return XRefAdaptor().fetch_all_by_ligand_id(self.ligand_id, *expressions)

    def get_proximal_water(self, *expressions):
        '''
        Returns all water atoms that are in contact with this ligand.

        Parameters
        ----------
        *expressions : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried Entities
        ----------------
        Subquery (not exposed), Atom, Residue

        Returns
        -------
        atoms : list
            List of `Atom` objects.

         Examples
        --------
        >>>
        '''
        return AtomAdaptor().fetch_all_water_by_ligand_id(self.ligand_id, *expressions)

    def get_ring_interactions(self, *expressions):
        '''
        '''
        return RingInteractionAdaptor().fetch_all_by_ligand_id(self.ligand_id, *expressions)

    def get_atom_ring_interactions(self, *expressions):
        '''
        Returns all the interactions between an atom and an aromatic ring.

        Parameters
        ----------
        *expressions : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried Entities
        ----------------
        AtomRingInteraction, AromaticRing

        Returns
        -------
        contacts : list
            List of `AtomRingInteraction` objects.

         Examples
        --------
        >>> self.get_atom_ring_interactions()
        [<AtomRingInteraction(22271)>, <AtomRingInteraction(22272)>,
         <AtomRingInteraction(22273)>, <AtomRingInteraction(22274)>,
         <AtomRingInteraction(22275)>, <AtomRingInteraction(22276)>,
         <AtomRingInteraction(22277)>]
        '''
        return AtomRingInteractionAdaptor().fetch_all_by_ligand_id(self.ligand_id, *expressions)

    def get_contacting_atoms(self, *expressions):
        '''
        Returns all atoms that are in contact with the ligand having the specified
        ligand identifier.

        Parameters
        ----------
        ligand_id : int
            `Ligand` identifier.
        *expressions : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried Entities
        ----------------
        Atom, binding_sites

        Returns
        -------
        atoms : list
            List of `Atom` objects.
        '''
        return AtomAdaptor().fetch_all_in_contact_with_ligand_id(self.ligand_id, *expressions)

    def get_contacting_residues(self, *expressions):
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
        return ResidueAdaptor().fetch_all_in_contact_with_ligand_id(self.ligand_id, *expressions)

    def usr(self, *expressions, **kwargs):
        '''
        Performs an Ultrast Shape Recognition (USR) search of this Ligand against
        either other Ligand or unbound conformers of chemical components.

        Parameters
        ----------
        limit : int, optional, default=25
            The number of hits that should be returned.
        target : {'ligands','chemcomps'}

        Returns
        -------
        hits : list

        See also
        --------

        References
        ----------
        Ballester, P. J. & Richards, G. W. Ultrafast shape recognition to search
        compound databases for similar molecular shapes. Journal of Computational
        Chemistry  28, 1711-1723 (2007).

        Examples
        --------

        '''
        # DO NOTHING IF THIS LIGAND DOES NOT HAVE ANY USR MOMENTS
        if not self.usr_space or not self.usr_moments: return None
        
        # DO A USR SEARCH AGAINST THE MODELLED CONFORMERS AND RETURN THE TOP RANKED CHEMCOMPS
        if kwargs.get('target', 'ligands') == 'chemcomps':
            return ChemCompAdaptor().fetch_all_by_usr_moments(*expressions, usr_space=self.usr_space, usr_moments=self.usr_moments, **kwargs)

        # DO A USR SEARCH AGAINST ALL BOUND LIGANDS
        else:
            return LigandAdaptor().fetch_all_by_usr_moments(*expressions, usr_space=self.usr_space, usr_moments=self.usr_moments, **kwargs)

from .ligandusr import LigandUSR
from .chemcompconformer import ChemCompConformer
from .chemcomp import ChemComp
from ..adaptors.chemcompadaptor import ChemCompAdaptor
from ..adaptors.xrefadaptor import XRefAdaptor
from ..adaptors.residueadaptor import ResidueAdaptor
from ..adaptors.atomadaptor import AtomAdaptor
from ..adaptors.contactadaptor import ContactAdaptor
from ..adaptors.aromaticringadaptor import AromaticRingAdaptor
from ..adaptors.ringinteractionadaptor import RingInteractionAdaptor
from ..adaptors.atomringinteractionadaptor import AtomRingInteractionAdaptor
from ..adaptors.ligandadaptor import LigandAdaptor