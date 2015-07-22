from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql.expression import and_, func, or_
from sqlalchemy.ext.hybrid import hybrid_method

from credoscript import Base, schema
from credoscript.mixins import PathMixin
from credoscript.util import rdkit, requires

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
    Biomolecule : Biomolecule
        Biological assembly this ligand is part of.
    Components : Query
        Chemical components this ligand consists of.
    Aromatic_rings : list
        All the aromatic rings of this ligand.
    Atoms : list
        All the atoms of this ligand.
    Ligand_fragments : Query
        All the fragments derived from this ligand.
    MolString : MolString
        Object containing the ligand structure in various formats as attributes.
    Residues : list
        Residues this ligand consists of.
    Xrefs : list
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
    __tablename__ = '%s.ligands' % schema['credo']

    Components = relationship("LigandComponent",
                              primaryjoin="LigandComponent.ligand_id==Ligand.ligand_id",
                              foreign_keys="[LigandComponent.ligand_id]",
                              uselist=True, innerjoin=True, lazy='dynamic',
                              backref=backref('Ligand', uselist=False, innerjoin=True))

    ChemComp = relationship("ChemComp",
                            primaryjoin="Ligand.ligand_name==ChemComp.het_id",
                            foreign_keys="[ChemComp.het_id]", uselist=False,
                            innerjoin=True)

    ChemComps = relationship("ChemComp",
                            secondary=Base.metadata.tables['%s.ligand_components' % schema['credo']],
                            primaryjoin="Ligand.ligand_id==LigandComponent.ligand_id",
                            secondaryjoin="LigandComponent.het_id==ChemComp.het_id",
                            foreign_keys="[LigandComponent.ligand_id, ChemComp.het_id]",
                            uselist=True, innerjoin=True, lazy='dynamic')

    # the residues this ligand consists of
    Residues = relationship("Residue",
                            secondary=Base.metadata.tables['%s.ligand_components' % schema['credo']],
                            primaryjoin="Ligand.ligand_id==LigandComponent.ligand_id",
                            secondaryjoin="LigandComponent.residue_id==Residue.residue_id",
                            foreign_keys="[LigandComponent.ligand_id, Residue.residue_id]",
                            uselist=True, innerjoin=True, lazy='dynamic',
                            backref=backref('LigandComponent', uselist=False, innerjoin=True))

    AromaticRings = relationship("AromaticRing",
                                  secondary=Base.metadata.tables['%s.ligand_components' % schema['credo']],
                                  primaryjoin="Ligand.ligand_id==LigandComponent.ligand_id",
                                  secondaryjoin="LigandComponent.residue_id==AromaticRing.residue_id",
                                  foreign_keys="[LigandComponent.ligand_id, AromaticRing.residue_id]",
                                  uselist=True, innerjoin=True, lazy='dynamic',
                                  backref=backref('LigandComponent', uselist=False, innerjoin=True))

    Atoms = relationship("Atom",
                         secondary=Base.metadata.tables['%s.ligand_components' % schema['credo']],
                         primaryjoin="Ligand.ligand_id==LigandComponent.ligand_id",
                         secondaryjoin="and_(LigandComponent.residue_id==Atom.residue_id, Ligand.biomolecule_id==Atom.biomolecule_id)",
                         foreign_keys="[LigandComponent.ligand_id, Atom.residue_id, Atom.biomolecule_id]",
                         uselist=True, innerjoin=True, lazy='dynamic')

    LigandFragments = relationship("LigandFragment",
                                   primaryjoin="LigandFragment.ligand_id==Ligand.ligand_id",
                                   foreign_keys="[LigandFragment.ligand_id]",
                                   uselist=True, innerjoin=True, lazy='dynamic',
                                   backref=backref('Ligand', uselist=False, innerjoin=True))

    XRefs = relationship("XRef",
                         primaryjoin="and_(XRef.entity_type=='Ligand', XRef.entity_id==Ligand.ligand_id)",
                         foreign_keys="[XRef.entity_type, XRef.entity_id]",
                         uselist=True, innerjoin=True, lazy='dynamic')

    MolString = relationship("LigandMolString",
                             primaryjoin="LigandMolString.ligand_id==Ligand.ligand_id",
                             foreign_keys="[LigandMolString.ligand_id]",
                             uselist=False,
                             backref=backref('Ligand', uselist=False, innerjoin=True))

    LigandUSR = relationship("LigandUSR",
                              primaryjoin="LigandUSR.ligand_id==Ligand.ligand_id",
                              foreign_keys="[LigandUSR.ligand_id]",
                              uselist=False,
                              backref=backref('Ligand', uselist=False, innerjoin=True))

    BindingSite = relationship("BindingSite",
                               primaryjoin="BindingSite.ligand_id==Ligand.ligand_id",
                               foreign_keys="[BindingSite.ligand_id]",
                               uselist=False,
                               backref=backref('Ligand', uselist=False, innerjoin=True))

    # these are the residues that are in contact with the ligand
    BindingSiteResidues = relationship("BindingSiteResidue",
                                       primaryjoin="BindingSiteResidue.ligand_id==Ligand.ligand_id",
                                       foreign_keys="[BindingSiteResidue.ligand_id]",
                                       uselist=True, innerjoin=True, lazy='dynamic',
                                       backref=backref('Ligand', uselist=False, innerjoin=True))

    # ligand efficiencies
    Effs = relationship("LigandEff",
                        primaryjoin="LigandEff.ligand_id==Ligand.ligand_id",
                        foreign_keys="[LigandEff.ligand_id]",
                        uselist=True, backref=backref('Ligand', uselist=False,
                                                      innerjoin=True))

    BindingSiteDomains = relationship("BindingSiteDomain",
                                       primaryjoin="BindingSiteDomain.ligand_id==Ligand.ligand_id",
                                       foreign_keys="[BindingSiteDomain.ligand_id]",
                                       uselist=True, innerjoin=True, lazy='dynamic',
                                       backref=backref('Ligand', uselist=False, innerjoin=True))

    DomainList = relationship("Domain",
                              secondary=Base.metadata.tables['%s.binding_site_domains' % schema['credo']],
                              primaryjoin="Ligand.ligand_id==BindingSiteDomain.ligand_id",
                              secondaryjoin="BindingSiteDomain.domain_id==Domain.domain_id",
                              foreign_keys="[BindingSiteDomain.ligand_id, Domain.domain_id]",
                              uselist=True)

    def __repr__(self):
        """
        """
        return '<Ligand({self.path})>'.format(self=self)

    def __len__(self):
        """
        Returns the number of heavy atoms of this ligand.
        """
        return self.num_hvy_atoms

    def __iter__(self):
        """
        Returns an iterator over the chemical components that this ligand consists
        of.
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
        if isinstance(other, Ligand) and self.usr_moments and other.usr_moments:
            ow, hw, rw, aw, dw = 1.0, 0.25, 0.25, 0.25, 0.25

            scale = 12 * (ow+hw+rw+aw+dw)
            weights = [abs(a - b) for a, b in zip(self.usr_moments, other.usr_moments)]

            # apply the USRCAT weights
            weights[:12] = [x*ow for x in weights[:12]]
            weights[12:24] = [x*hw for x in weights[12:24]]
            weights[24:36] = [x*rw for x in weights[24:36]]
            weights[36:48] = [x*aw for x in weights[36:48]]
            weights[48:] = [x*dw for x in weights[48:]]

            return  1.0 / (1.0 + sum(weights) / scale)

    @requires.rdkit
    def __mod__(self, other):
        '''
        Returns the tanimoto similarity between two chemical components.
        Overloads '%' operator.

        Returns
        -------
        tanimoto : float
            The 2D Tanimoto similarity between two RDKit torsion fingerprints of
            the chemical components.

        Requires
        --------
        .. important:: `RDKit  <http://www.rdkit.org>`_ Python wrappers.
        '''
        if isinstance(other, Ligand):
            return rdkit.tanimoto_sml(self.MolString.ism, other.MolString.ism)

    @property
    def name(self):
        """
        Alias for ligand_name.
        """
        return self.ligand_name

    @hybrid_method
    @property
    def is_enzyme_cmpd(self):
        """
        Meta Boolean flag indicating whether the ligand is the enzyme's substrate
        or product or not.
        """
        return any((self.is_product==True, self.is_substrate==True))

    @is_enzyme_cmpd.expression
    @property
    def is_enzyme_cmpd(self):
        """
        Returns an SQLAlchemy boolean clause list that enables usage of this
        meta ligand flag to filter query constructs.
        """
        return or_(Ligand.is_product==True, Ligand.is_substrate==True)

    @property
    def Contacts(self):
        """
        Returns Query.
        """
        adaptor = ContactAdaptor(dynamic=True)
        return adaptor.fetch_all_by_ligand_id(self.ligand_id,
                                              self.biomolecule_id)
    @property
    def RingInteractions(self):
        """
        """
        adaptor = RingInteractionAdaptor(dynamic=True)
        return adaptor.fetch_all_by_ligand_id(self.ligand_id)

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
        adaptor = AtomRingInteractionAdaptor(dynamic=True)
        return adaptor.fetch_all_by_ligand_id(self.ligand_id)

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
        adaptor = AtomAdaptor(dynamic=True)
        return adaptor.fetch_all_water_in_contact_with_ligand_id(self.ligand_id,
                                                                 self.biomolecule_id)

    @property
    def ProximalProtFragments(self):
        """
        """
        adaptor = ProtFragmentAdaptor(dynamic=True)
        return adaptor.fetch_all_in_contact_with_ligand_id(self.ligand_id)

    @property
    def ProximalResidues(self):
        """
        Returns all residues that are in contact with the ligand having the specified
        ligand identifier.
        """
        adaptor = ResidueAdaptor(dynamic=True)
        return adaptor.fetch_all_in_contact_with_ligand_id(self.ligand_id)

    @property
    def ProximalAtoms(self):
        """
        Returns all atoms that are in contact with the ligand having the specified
        ligand identifier.
        """
        adaptor = AtomAdaptor(dynamic=True)
        return adaptor.fetch_all_in_contact_with_ligand_id(self.ligand_id,
                                                           self.biomolecule_id)

    @property
    def usr_space(self):
        """
        """
        if self.LigandUSR:
            return self.LigandUSR.usr_space

    @property
    def usr_moments(self):
        """
        """
        if self.LigandUSR:
            return self.LigandUSR.usr_moments

    def sift(self, *expr, **kwargs):
        """
        """
        return SIFtAdaptor().fetch_by_ligand_id(self.ligand_id, self.biomolecule_id,
                                                *expr)

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

        # choose which surface state should be used
        if state == 'delta': column = BindingSiteAtomSurfaceArea.asa_delta
        elif state == 'apo': column = BindingSiteAtomSurfaceArea.asa_apo
        elif state == 'bound': column = BindingSiteAtomSurfaceArea.asa_bound

        # return the atoms and the individual change in solvent-accessible
        # surface area
        if atom_areas:
            query = session.query(Atom, BindingSiteAtomSurfaceArea.asa_delta)

        # return the sum of the atom surface area contributions
        else:
            buried_area = func.sum(column).label('buried_surface_area')
            query = session.query(buried_area).select_from(Atom)

            # use the partition constraint-exclusion of the atoms table!
            query = query.filter(Atom.biomolecule_id==self.biomolecule_id)

        query = query.join(binding_site_atom_surface_areas,
                           BindingSiteAtomSurfaceArea.atom_id==Atom.atom_id)

        # only include ligand atoms
        if projection == 'ligand':
            query = query.join(Residue, Residue.residue_id==Atom.residue_id)
            query = query.filter(Residue.entity_type_bm.op('&')(2) > 0)

        # only include polymer atoms that form the binding site
        elif projection == 'bindingsite':
            query = query.join(Residue, Residue.residue_id==Atom.residue_id)
            query = query.filter(Residue.entity_type_bm.op('&')(3) == 0)

        query = query.filter(and_(BindingSiteAtomSurfaceArea.ligand_id==self.ligand_id,
                                  *expr))

        # consider only polar atoms in surface areas
        if polar: query = query.filter(Atom.is_polar==True)

        # return simple scalar or list for the atoms
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
        # do nothing if this ligand does not have any usr moments
        if not self.usr_space or not self.usr_moments: return None

        # do a USR search against the modelled conformers and return the top
        # ranked chemcomps
        if kwargs.get('target', 'ligands') == 'chemcomps':
            return ChemCompAdaptor().fetch_all_by_usr_moments(*expr,
                                                              usr_space=self.usr_space,
                                                              usr_moments=self.usr_moments,
                                                              **kwargs)

        # do a USR search against all bound ligands
        else:
            return LigandAdaptor().fetch_all_by_usr_moments(*expr,
                                                            usr_space=self.usr_space,
                                                            usr_moments=self.usr_moments,
                                                            **kwargs)

from .atom import Atom
from .residue import Residue
#from .bindingsite import BindingSiteAtomSurfaceArea
from ..adaptors.chemcompadaptor import ChemCompAdaptor
from ..adaptors.residueadaptor import ResidueAdaptor
from ..adaptors.atomadaptor import AtomAdaptor
from ..adaptors.contactadaptor import ContactAdaptor
from ..adaptors.ringinteractionadaptor import RingInteractionAdaptor
from ..adaptors.atomringinteractionadaptor import AtomRingInteractionAdaptor
from ..adaptors.ligandadaptor import LigandAdaptor
from ..adaptors.protfragmentadaptor import ProtFragmentAdaptor
from ..adaptors.siftadaptor import SIFtAdaptor
