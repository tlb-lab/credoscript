from warnings import warn

from sqlalchemy.orm import aliased, backref, relationship
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.sql.expression import and_, func, text
from sqlalchemy.ext.hybrid import hybrid_method

from credoscript import Base, session
from credoscript.support import requires

class ChemComp(Base):
    '''
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
    Conformers : list
        All Conformers that were modelled for this chemical component. Includes
        conformer-dependent information such as surface areas and shape descriptors.
    ChemCompFragments : list
        Entities derived from the mapping between Fragments and Chemical Components.
    Fragments : list
        All unique Fragments of this Chemical Component created through RECAP
        fragmentation.
    XRefs : list
        CREDO XRef objects that are associated with this Chemical Component.

    See Also
    --------
    ChemCompAdaptor : Fetch ChemComps from the database.

    Notes
    -----
    - The __mod__ (%) method is overloaded for this class and will return the
      tanimoto similarity between this and another chemical component from CREDO.
    '''
    __tablename__ = 'pdbchem.chem_comps'
    
    ChemCompFragments = relationship("ChemCompFragment",
                                     primaryjoin="ChemCompFragment.het_id==ChemComp.het_id",
                                     foreign_keys = "[ChemCompFragment.het_id]",
                                     uselist=True, innerjoin=True,
                                     backref=backref('ChemComp', uselist=False, innerjoin=True))
    
    Conformers = relationship("ChemCompConformer",
                              primaryjoin="ChemCompConformer.het_id==ChemComp.het_id",
                              foreign_keys = "[ChemCompConformer.het_id]",
                              uselist=True, innerjoin=True,
                              backref=backref('ChemComp', uselist=False, innerjoin=True))     
    
    Fragments = relationship("Fragment",
                             secondary=Base.metadata.tables['pdbchem.chem_comp_fragments'],
                             primaryjoin="ChemComp.het_id==ChemCompFragment.het_id",
                             secondaryjoin="ChemCompFragment.fragment_id==Fragment.fragment_id",
                             foreign_keys="[ChemCompFragment.het_id, Fragment.fragment_id]",
                             uselist=True, innerjoin=True,
                             backref = backref('ChemComps', uselist=True, innerjoin=True))   
    
    XRefs = relationship("XRef", collection_class=attribute_mapped_collection("source"),
                         primaryjoin="and_(XRef.entity_type=='ChemComp', XRef.entity_id==ChemComp.chem_comp_id)",
                         foreign_keys="[XRef.entity_type, XRef.entity_id]",
                         uselist=True, innerjoin=True)    
    
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
        '''
        '''
        return '<ChemComp({self.het_id})>'.format(self=self)

    def __len__(self):
        '''
        Returns the number of heavy atoms of this chemical component.

        Returns
        -------
        num_hvy_atoms : int
            Number of heavy atoms of this chemical component.

        Notes
        -----
        - Overloads len() function.
        '''
        return self.num_hvy_atoms

    @requires.rdkit_catridge
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
        .. important:: `RDKit  <http://www.rdkit.org>`_ PostgreSQL cartridge.
        '''
        if isinstance(other, ChemComp):
            fp1,fp2 = aliased(ChemCompRDFP), aliased(ChemCompRDFP)

            query = session.query(func.rdkit.tanimoto_sml(fp1.torsion_fp, fp2.torsion_fp))
            query = query.filter(and_(fp1.het_id==self.het_id, fp2.het_id==other.het_id))

            return query.scalar()

    @classmethod
    def like(self, smiles):
        '''
        Returns an SQL function expression that uses the PostgreSQL trigram index
        to compare the SMILES strings.
        '''
        return self.ism.op('%%')(smiles)

from .chemcomprdfp import ChemCompRDFP