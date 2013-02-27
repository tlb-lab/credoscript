from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection

from credoscript import Base
from credoscript.mixins import PathMixin, ResidueMixin

class Peptide(Base, PathMixin, ResidueMixin):
    '''
    Represents a PDB polypeptide Residue.

    Attributes
    ----------
    residue_id : int
        Primary key.
    biomolecule_id : int
        Primary key of the parent biomolecule.
    chain_id : int
        Primary key of the parent chain.
    path : str
        ptree
    res_name : str
        Three-letter name of the residue.
    res_num : int
        PDB residue number.
    ins_code : str
        PDB insertion code.
    entity_type_bm : int
        Entity type bitmask (the bits are solvent, ligand, saccharide, rna, dna,
        protein).
    is_clashing : bool

    is_disordered : bool
        True if the residue has disordered atoms.
    is_incomplete : bool
        True if the residue has missing atoms.
    res_map_id : int-
        Primary key of this peptide in the SIFTS residue mapping.
    one_letter_code : str
        One-letter code of the amino acid. X is used in case of non-standard
        amino acids.
    sstruct : str
        Secondary structure DSSP code.
    cath : str
        CATH domain identifier.
    px : int
        SCOP px identifier.
    is_non_std : bool
        True if the residue is not one of the 20 standard amino acids.
    is_modified : bool
        True if this peptide is modified according to the SIFTS residue mapping.
    is_mutated : bool
        True if this peptide is one of the 20 standard amino acids and the but
        differs from the canonical UniProt amino acid for this position.

    Mapped attributes
    -----------------
    Rings : Query
        AromaticRings of this Residue in case is it aromatic.
    Atoms : Query
        Atoms of this Residue.
    XRefs : Query
        CREDO XRef objects that are associated with this Residue Entity.

    Notes
    -----
    The __getitem__ method is overloaded to allow accessing Atoms directly by
    their names, e.g. Residue['CA']. Returns a list due to atoms with
    possible alternate locations.
    '''
    __tablename__ = 'credo.peptides'

    ResMap = relationship("ResMap",
                           primaryjoin="ResMap.res_map_id==Peptide.res_map_id",
                           foreign_keys="[ResMap.res_map_id]",
                           uselist=False, innerjoin=True)

    Domains = relationship("Domain",
                           secondary=Base.metadata.tables['credo.domain_peptides'],
                           primaryjoin="Peptide.residue_id==DomainPeptide.residue_id",
                           secondaryjoin="DomainPeptide.domain_id==Domain.domain_id",
                           foreign_keys="[DomainPeptide.domain_id, DomainPeptide.residue_id]",
                           uselist=True, innerjoin=True, lazy='dynamic')

    Features = relationship("PeptideFeature",
                            primaryjoin="PeptideFeature.res_map_id==Peptide.res_map_id",
                            foreign_keys="[PeptideFeature.res_map_id]", lazy='dynamic',
                            uselist=True)

    FeatureList = relationship("PeptideFeature",
                               primaryjoin="PeptideFeature.res_map_id==Peptide.res_map_id",
                               foreign_keys="[PeptideFeature.res_map_id]",
                               uselist=True)

    FeatureMap = relationship("PeptideFeature",
                              collection_class=attribute_mapped_collection('feature_type'),
                              primaryjoin="PeptideFeature.res_map_id==Peptide.res_map_id",
                              foreign_keys="[PeptideFeature.res_map_id]",
                              uselist=True, innerjoin=True)

    @property
    def Variations(self):
        """
        """
        return VariationAdaptor().fetch_all_by_res_map_id(self.res_map_id)

    @property
    def Contacts(self):
        """
        """
        adaptor = ContactAdaptor(dynamic=True)
        return adaptor.fetch_all_by_residue_id(self.residue_id, self.biomolecule_id)

class PeptideFeature(Base):
    """
    """
    __tablename__ = 'credo.peptide_features'

    def __repr__(self):
        """
        """
        return "<PeptideFeature({self.feature_type})>".format(self=self)

from .atom import Atom
from ..adaptors.contactadaptor import ContactAdaptor
from ..adaptors.variationadaptor import VariationAdaptor
