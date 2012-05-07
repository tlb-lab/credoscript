from sqlalchemy.orm import backref, deferred, relationship
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.sql.expression import and_, cast, func
from sqlalchemy.dialects.postgresql import INTEGER

from credoscript import (Base, Session, binding_sites, ligand_usr, binding_site_atom_surface_areas)
from credoscript.mixins import PathMixin

class Ligand(Base, PathMixin):
    """
    Represents a `Ligand` entity from CREDO. A `Ligand` object in CREDO can consist
    of more than one chemical component (maximum 10).

    Attributes
    ----------
    ligand_id : int
        Primary key of this object.
    biomolecule_id : int
        "Foreign key" of the parent `Biomolecule` (Structure.id).
    entity_serial : int
        Serial number of the ligand as entity. Only used internally for inserts,
        updates, etc.
    pdb_chain_id : string
        PDB chain identifier of this Ligand.
    ligand_name : string
        String consisting of the concatenated chemical component names (HET ID)
        of all `LigandComponent` objects.
    res_num : int or None
        PDB residue number. None in case of a `Ligand` with more than one
        `LigandComponent`.
    num_hvy_atoms : int
        Number of all observed heavy atoms of this Ligand.
    gini_index_contacts : float
        Gini index for the contacts that the ligand atom form with other atoms.
    is_at_identity : bool
        True if the ligand is at identity, i.e. no transformation was performed.
    is_incomplete : bool
        Boolean flag indicating whether this Ligand has missing (not observed)
        atoms.
    is_disordered : bool
        True if at least one ligand atom is disordered.
    is_clashing : bool
        True if the ligand is clashing with other residues.
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
    biomolecule : Biomolecule
        Biological assembly this ligand is part of.
    components : Query
        Chemical components this ligand consists of.
    aromatic_rings : list
        All the aromatic rings of this ligand.
    atoms : list
        All the atoms of this ligand.
    ligand_fragments : Query
        All the fragments derived from this ligand.
    molstring : MolString
        Object containing the ligand structure in various formats as attributes.
    residues : list
        Residues this ligand consists of.
    xrefs : list
        Cross references to external databases.

    Overloaded operators
    --------------------
    __or__
        Returns the USR similarity between this and another Ligand
        (Overloads | operator).

    See Also
    --------
    LigandAdaptor : Fetch Ligands from the database.
    """
    __tablename__ = 'credo.ligands'

    Components = relationship("LigandComponent",
                              primaryjoin = "LigandComponent.ligand_id==Ligand.ligand_id",
                              foreign_keys = "[LigandComponent.ligand_id]",
                              uselist=True, innerjoin=True, lazy='dynamic',
                              backref=backref('Ligand', uselist=False, innerjoin=True))

    Residues = relationship("Residue",
                            secondary = Base.metadata.tables['credo.ligand_components'],
                            primaryjoin = "Ligand.ligand_id==LigandComponent.ligand_id",
                            secondaryjoin = "LigandComponent.residue_id==Residue.residue_id",
                            foreign_keys = "[LigandComponent.ligand_id, Residue.residue_id]",
                            uselist=False, innerjoin=True, lazy='dynamic',
                            backref=backref('LigandComponent', uselist=False, innerjoin=True))

    AromaticRings = relationship("AromaticRing",
                                  secondary = Base.metadata.tables['credo.ligand_components'],
                                  primaryjoin = "Ligand.ligand_id==LigandComponent.ligand_id",
                                  secondaryjoin = "LigandComponent.residue_id==AromaticRing.residue_id",
                                  foreign_keys = "[LigandComponent.ligand_id, AromaticRing.residue_id]",
                                  uselist=False, innerjoin=True, lazy='dynamic',
                                  backref=backref('LigandComponent', uselist=False, innerjoin=True))

    Atoms = relationship("Atom",
                         secondary = Base.metadata.tables['credo.ligand_components'],
                         primaryjoin = "Ligand.ligand_id==LigandComponent.ligand_id",
                         secondaryjoin = "and_(LigandComponent.residue_id==Atom.residue_id, Ligand.biomolecule_id==Atom.biomolecule_id)",
                         foreign_keys = "[LigandComponent.ligand_id, Atom.residue_id, Atom.biomolecule_id]",
                         uselist=False, innerjoin=True, lazy='dynamic')

    LigandFragments = relationship("LigandFragment",
                                   primaryjoin = "LigandFragment.ligand_id==Ligand.ligand_id",
                                   foreign_keys = "[LigandFragment.ligand_id]",
                                   uselist=True, innerjoin=True, lazy='dynamic',
                                   backref=backref('Ligand', uselist=False, innerjoin=True))

    XRefs = relationship("XRef",
                         primaryjoin = "and_(XRef.entity_type=='Ligand', XRef.entity_id==Ligand.ligand_id)",
                         foreign_keys = "[XRef.entity_type, XRef.entity_id]",
                         uselist=True, innerjoin=True, lazy='dynamic')

    MolString = relationship("LigandMolString",
                             primaryjoin = "LigandMolString.ligand_id==Ligand.ligand_id",
                             foreign_keys = "[LigandMolString.ligand_id]",
                             uselist=False, innerjoin=True,
                             backref=backref('Ligand', uselist=False, innerjoin=True))

    def __repr__(self):
        """
        """
        return '<Ligand({self.pdb_chain_id} {self.res_num} {self.ligand_name})>'.format(self=self)

    def __len__(self):
        """
        """
        return self.num_hvy_atoms

    def __iter__(self):
        """
        """
        return iter(self.Components)

    def __or__(self, other):
        """
        Returns the USR similarity between this and another Ligand. Overloads '|'
        operator.

        Returns
        -------
        usr : float
            The USR similarity between two ligands.
        """
        if isinstance(other, Ligand):
            if self.usr_space and other.usr_space:
                distance = sum([abs(a - b) for a, b in zip(self.usr_space, other.usr_space)])
                return 1.0 / (1.0 + distance / 12.0)

    @property
    def Contacts(self):
        """
        Returns Query.
        """
        return ContactAdaptor().fetch_all_by_ligand_id(self.ligand_id,
                                                       self.biomolecule_id,
                                                       dynamic=True)

    @property
    def RingInteractions(self):
        """
        """
        return RingInteractionAdaptor().fetch_all_by_ligand_id(self.ligand_id,
                                                               dynamic=True)

    @property
    def AtomRingInteractions(self):
        """
        Returns all the interactions between an atom and an aromatic ring.

        Parameters
        ----------
        *expr : BinaryExpressions, optional
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
        """
        return AtomRingInteractionAdaptor().fetch_all_by_ligand_id(self.ligand_id,
                                                                   dynamic=True)

    @property
    def ProximalWater(self):
        """
        Returns all water atoms that are in contact with this ligand.

        Parameters
        ----------
        *expr : BinaryExpressions, optional
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
        """
        return AtomAdaptor().fetch_all_water_in_contact_with_ligand_id(self.ligand_id,
                                                                       self.biomolecule_id,
                                                                       dynamic=True)

    @property
    def ProximalProtFragments(self):
        """
        """
        return ProtFragmentAdaptor().fetch_all_in_contact_with_ligand_id(self.ligand_id,
                                                                         dynamic=True)

    @property
    def ProximalResidues(self):
        """
        Returns all residues that are in contact with the ligand having the specified
        ligand identifier.

        Parameters
        ----------
        ligand_id : int
            `Ligand` identifier.
        *expr : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried Entities
        ----------------
        Residue, binding_sites

        Returns
        -------
        residues : list
            List of `Residue` objects.
        """
        return ResidueAdaptor().fetch_all_in_contact_with_ligand_id(self.ligand_id,
                                                                    dynamic=True)

    @property
    def ProximalAtoms(self):
        """
        Returns all atoms that are in contact with the ligand having the specified
        ligand identifier.

        Parameters
        ----------
        ligand_id : int
            `Ligand` identifier.
        *expr : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried Entities
        ----------------
        Atom, binding_sites

        Returns
        -------
        atoms : list
            List of `Atom` objects.
        """
        return AtomAdaptor().fetch_all_in_contact_with_ligand_id(self.ligand_id,
                                                                 self.biomolecule_id,
                                                                 dynamic=True)

    @property
    def usr_space(self):
        """
        """
        session = Session()

        return session.query(ligand_usr.c.usr_space).filter(
            ligand_usr.c.ligand_id==self.ligand_id).scalar()

    @property
    def usr_moments(self):
        """
        """
        session = Session()

        return session.query(ligand_usr.c.usr_moments).filter(
            ligand_usr.c.ligand_id==self.ligand_id).scalar()

    def sift(self, *expr, **kwargs):
        """
        """
        return SIFtAdaptor().fetch_by_ligand_id(self.ligand_id, self.biomolecule_id, *expr)

    def buried_surface_area(self, *expr, **kwargs):
        """
        Returns the buried solvent-accessible surface areas of the ligand.

        Parameters
        ----------
        *expr : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.
        state: str, {'apo','bound','delta'}, default='delta'
            State of the surface.
        atom_areas: bool, default=False
            If True, the method returns the Atoms and their change in solvent-accessible
            surface area for the given projection - otherwise the sum of the individual
            contributions.
        projection: str, {'complex','ligand','bindingsite'}
            The entity for which the surface area should be returned:
            - complex: all atoms
            - ligand: only ligand atoms
            - bindingsite: all the atoms the ligand is in contact with

        Queried Entities
        ----------------
        binding_site_atom_surface_areas, Atom, Residue

        Returns
        -------

        Examples
        --------

        """
        state = kwargs.get('state','delta')
        atom_areas = kwargs.get('atom_areas', False)
        projection = kwargs.get('projection','complex')
        polar = kwargs.get('polar', False)

        # CHOOSE WHICH SURFACE STATE SHOULD BE USED
        if state == 'delta': column = binding_site_atom_surface_areas.c.asa_delta
        elif state == 'apo': column = binding_site_atom_surface_areas.c.asa_apo
        elif state == 'bound': column = binding_site_atom_surface_areas.c.asa_bound

        # RETURN THE ATOMS AND THE INDIVIDUAL CHANGE IN SOLVENT-ACCESSIBLE SURFACE AREA
        if atom_areas:
            query = session.query(Atom, binding_site_atom_surface_areas.c.asa_delta)

        # RETURN THE SUM OF THE ATOM SURFACE AREA CONTRIBUTIONS
        else:
            buried_area = func.sum(column).label('buried_surface_area')
            query = session.query(buried_area).select_from(Atom)

            # USE THE PARTITION CONSTRAINT-EXCLUSION OF THE ATOMS TABLE!
            query = query.filter(Atom.biomolecule_id==self.biomolecule_id)

        query = query.join(binding_site_atom_surface_areas,
                           binding_site_atom_surface_areas.c.atom_id==Atom.atom_id)

        # ONLY INCLUDE LIGAND ATOMS
        if projection == 'ligand':
            query = query.join(Residue, Residue.residue_id==Atom.residue_id)
            query = query.filter(Residue.entity_type_bm.op('&')(2) > 0)

        # ONLY INCLUDE POLYMER ATOMS THAT FORM THE BINDING SITE
        elif projection == 'bindingsite':
            query = query.join(Residue, Residue.residue_id==Atom.residue_id)
            query = query.filter(Residue.entity_type_bm.op('&')(3) == 0)

        query = query.filter(and_(binding_site_atom_surface_areas.c.ligand_id==self.ligand_id,
                                  *expr))

        # CONSIDER ONLY POLAR ATOMS IN SURFACE AREAS
        if polar: query = query.filter(Atom.is_polar==True)

        # RETURN SIMPLE SCALAR OR LIST FOR THE ATOMS
        if not atom_areas: result = query.scalar()
        else: result = query.all()

        return result

    def usrcat(self, *expr, **kwargs):
        """
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

        """
        # DO NOTHING IF THIS LIGAND DOES NOT HAVE ANY USR MOMENTS
        if not self.usr_space or not self.usr_moments: return None

        # DO A USR SEARCH AGAINST THE MODELLED CONFORMERS AND RETURN THE TOP RANKED CHEMCOMPS
        if kwargs.get('target', 'ligands') == 'chemcomps':
            return ChemCompAdaptor().fetch_all_by_usr_moments(*expr, usr_space=self.usr_space, usr_moments=self.usr_moments, **kwargs)

        # DO A USR SEARCH AGAINST ALL BOUND LIGANDS
        else:
            return LigandAdaptor().fetch_all_by_usr_moments(*expr, usr_space=self.usr_space, usr_moments=self.usr_moments, **kwargs)

from .ligandusr import LigandUSR
from .chemcomp import ChemComp
from .atom import Atom
from .contact import Contact
from .residue import Residue
from ..adaptors.chemcompadaptor import ChemCompAdaptor
from ..adaptors.xrefadaptor import XRefAdaptor
from ..adaptors.residueadaptor import ResidueAdaptor
from ..adaptors.atomadaptor import AtomAdaptor
from ..adaptors.contactadaptor import ContactAdaptor
from ..adaptors.aromaticringadaptor import AromaticRingAdaptor
from ..adaptors.ringinteractionadaptor import RingInteractionAdaptor
from ..adaptors.atomringinteractionadaptor import AtomRingInteractionAdaptor
from ..adaptors.ligandadaptor import LigandAdaptor
from ..adaptors.protfragmentadaptor import ProtFragmentAdaptor
from ..adaptors.siftadaptor import SIFtAdaptor