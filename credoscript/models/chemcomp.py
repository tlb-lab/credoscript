from sqlalchemy.orm import aliased, backref, relationship
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.sql.expression import and_, func
from sqlalchemy.ext.hybrid import hybrid_method

from credoscript import Base, schema
from credoscript.util import rdkit, requires

class ChemComp(Base):
    """
    Represents a chemical component entity from the PDB with additional calculated
    chemical properties.

    Attributes
    ----------
    chem_comp_id : int
        Primary key.
    het_id : str
        PDB identifier of the chemical component. The predecessor of PDBeChem
        included amino acid variants that had HET-IDs with more than three characters,
        that's why the separation is still here.
    three_letter_code : str
        Three-letter version of the the HET-ID.
    replaced_by_het_id : str
        Indicates by which chemical component this one has be been replaced
    nstd_parent_het_id : str
        HET-ID(s) of the chemical component this one is derived from, e.g. in case
        of modified amino acids this field will link to the standard version.
    iupac_name : str
        IUPAC systematic name.
    initial_date :

    modified_date :

    ism : str
        Isomeric SMILES string of the chemical component.
    mw : float
        Molecular weight.
    num_hvy_atoms : int
        Number of non-hydrogen atoms.
    num_carbons : int
        Number of carbon atoms.
    num_heteroatoms : int
        Number of non-carbon atoms.
    num_halides : int
        Number of halogen atoms.
    het_carb_ratio : float
        Ratio between the number of hetero and carbon atoms.
    formal_charge_count : int
        Number of formal charges in the chemical structure.
    formal_charge_sum : int
        Sum of the formal charges.
    num_chiral_centers : int
        Number of stereocenters.
    num_bonds : int
        Number of bonds.
    num_rotors : int
        Number of rotatable bonds.
    num_ringsystems : int
        Number of ring systems.
    num_arom_ringsystems : int
        Number of aromatic ring systems.
    num_lipinski_hbond_acceptors : int
        Number of Lipinski hydrogen bond acceptors.
    num_lipinski_hbond_donors : int
        Number of Lipinski hydrogen bond donors.
    tpsa : float
        Topological polar surface area (PSA)
    xlogp : float
        XLogP.
    fraction_csp3 : float
        Number of sp3 carbons divided by the total number of carbons.
    has_std_atoms : boolean
        True if the chemical component only has standard organic element atoms.
    has_butyl : boolean
        True if the chemical component has a butyl chain in its structure.
    is_amino_acid : boolean
        True if the chemical component is a standard amino acid or derived from one.
    is_nucleotide : boolean
        True if the chemical component is a nucleotide or derived from one.
    is_saccharide : boolean
        True if the chemical component
    is_nat_product : boolean
        True if the chemical component
    is_metabolite : boolean
        True if the chemical component
    is_drug_like : boolean
        True if the chemical component is drug-like.
    is_drug : boolean
        True if the chemical component is a drug (not necessarily approved).
    is_approved_drug : boolean
        True if the chemical component is an approved drug.

    Mapped Attributes
    -----------------
    Conformers : Query
        All Conformers that were modelled for this chemical component. Includes
        conformer-dependent information such as surface areas and shape descriptors.
    ChemCompFragments : Query
        Entities derived from the mapping between Fragments and Chemical Components.
    Fragments : Query
        All unique Fragments of this Chemical Component created through RECAP
        fragmentation.
    Ligands : Query

    XRefs : Query
        CREDO XRef objects that are associated with this Chemical Component.

    See Also
    --------
    ChemCompAdaptor : Fetch chemical components from the database.

    Notes
    -----
    - The __mod__ (%) method is overloaded for this class and will return the
      tanimoto similarity between this and another chemical component from CREDO.
    """
    __tablename__ = '%s.chem_comps' % schema['pdbchem']

    ChemCompFragments = relationship("ChemCompFragment",
                                     primaryjoin="ChemCompFragment.het_id==ChemComp.het_id",
                                     foreign_keys = "[ChemCompFragment.het_id]",
                                     uselist=True, innerjoin=True, lazy='dynamic',
                                     backref=backref('ChemComp', uselist=False, innerjoin=True))

    Conformers = relationship("ChemCompConformer",
                              primaryjoin="ChemCompConformer.het_id==ChemComp.het_id",
                              foreign_keys = "[ChemCompConformer.het_id]",
                              uselist=True, innerjoin=True, lazy='dynamic',
                              backref=backref('ChemComp', uselist=False, innerjoin=True))

    Fragments = relationship("Fragment",
                             secondary=Base.metadata.tables['%s.chem_comp_fragments' % schema['pdbchem']],
                             primaryjoin="ChemComp.het_id==ChemCompFragment.het_id",
                             secondaryjoin="ChemCompFragment.fragment_id==Fragment.fragment_id",
                             foreign_keys="[ChemCompFragment.het_id, Fragment.fragment_id]",
                             lazy='dynamic', uselist=True, innerjoin=True)

    Ligands = relationship("Ligand",
                           primaryjoin="Ligand.ligand_name==ChemComp.het_id",
                           foreign_keys = "[Ligand.ligand_name]",
                           lazy='dynamic', uselist=True, innerjoin=True)

    XRefs = relationship("XRef",
                         primaryjoin="and_(XRef.entity_type=='ChemComp', XRef.entity_id==ChemComp.chem_comp_id)",
                         foreign_keys="[XRef.entity_type, XRef.entity_id]",
                         lazy='dynamic', uselist=True, innerjoin=True)

    XRefMap = relationship("XRef",
                            collection_class=attribute_mapped_collection("source"),
                            primaryjoin="and_(XRef.entity_type=='ChemComp', XRef.entity_id==ChemComp.chem_comp_id)",
                            foreign_keys="[XRef.entity_type, XRef.entity_id]",
                            uselist=True, innerjoin=True)

    MolString = relationship("ChemCompMolString",
                             primaryjoin="ChemCompMolString.het_id==ChemComp.het_id",
                             foreign_keys = "[ChemCompMolString.het_id]",
                             uselist=False, innerjoin=True)

    RDMol = relationship("ChemCompRDMol",
                         primaryjoin="ChemCompRDMol.het_id==ChemComp.het_id",
                         foreign_keys="[ChemCompRDMol.het_id]",
                         uselist=False, innerjoin=True,
                         backref=backref('ChemComp', uselist=False, innerjoin=True))

    RDFP = relationship("ChemCompRDFP",
                        primaryjoin="ChemCompRDFP.het_id==ChemComp.het_id",
                        foreign_keys="[ChemCompRDFP.het_id]",
                        uselist=False, innerjoin=True,
                        backref=backref('ChemComp', uselist=False, innerjoin=True))

    def __repr__(self):
        """
        """
        return '<ChemComp({self.het_id})>'.format(self=self)

    def __len__(self):
        """
        Returns the number of heavy atoms of this chemical component.

        Returns
        -------
        num_hvy_atoms : int
            Number of heavy atoms of this chemical component.

        Notes
        -----
        - Overloads len() function.
        """
        return self.num_hvy_atoms

    def __or__(self, other):
        """
        Returns the maximum USRCAT similarity between the LEC (Lowest Energy
        Conformer) of this chemical component and all of the other.

        Overloads '|' operator.

        Returns
        -------
        usr : float
            The maximum USR similarity between the two chemical components.
        """
        if isinstance(other, ChemComp):
            M2 = aliased(ChemCompConformer)

            sim = func.arrayxd_usrcatsim(ChemCompConformer.usr_moments,
                                         M2.usr_moments,
                                         1.0, 0.25, 0.25, 0.25, 0.25)

            query = ChemCompConformer.query
            query = query.with_entities(func.max(sim))
            query = query.filter(and_(ChemCompConformer.het_id==self.het_id,
                                      ChemCompConformer.conformer==1,
                                      M2.het_id==other.het_id))

            return query.scalar()

    @requires.rdkit
    def __mod__(self, other):
        """
        Returns the tanimoto similarity between two chemical components.
        Overloads '%' operator.

        Returns
        -------
        tanimoto : float
            The 2D Tanimoto similarity between two RDKit circular fingerprints of
            the chemical components.

        Requires
        --------
        .. important:: `RDKit  <http://www.rdkit.org>`_ PostgreSQL cartridge.
        """
        if isinstance(other, ChemComp):
            return rdkit.tanimoto_sml(self.ism, other.ism)

    @classmethod
    def like(self, smiles):
        """
        Returns an SQL function expression that uses the PostgreSQL trigram index
        to compare the SMILES strings.
        """
        return self.ism.op('%%')(smiles)

    @hybrid_method
    @property
    def is_het_peptide(self):
        """
        Meta column type indicating whether the chemical component is a heteropeptide
        or not, i.e. if it consists of subcomponents according to the PDB.
        """
        return bool(self.subcomponents)

    @is_het_peptide.expression
    @property
    def is_het_peptide(self):
        """
        Returns an SQLAlchemy boolean clause list that can enables usage of this
        meta atom type to filter query constructs.
        """
        return ChemComp.subcomponents!=None

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
        conformer = self.Conformers.first()

        return ChemCompAdaptor().fetch_all_by_usr_moments(*expr, usr_space=conformer.usr_space,
                                                          usr_moments=conformer.usr_moments,
                                                          **kwargs)

from .chemcompconformer import ChemCompConformer
from ..adaptors.chemcompadaptor import ChemCompAdaptor
