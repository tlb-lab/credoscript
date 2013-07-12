from contextlib import closing

from sqlalchemy import func
from sqlalchemy.orm import relationship, backref

from credoscript import Base, Session

class BindingSite(Base):
    """
    Represents a unique protein-ligand binding site.
    """
    __tablename__ = 'credo.binding_sites'

    Domains = relationship("Domain",
                           secondary=Base.metadata.tables['credo.binding_site_domains'],
                            primaryjoin="BindingSite.ligand_id==BindingSiteDomain.ligand_id",
                            secondaryjoin="BindingSiteDomain.domain_id==Domain.domain_id",
                            foreign_keys="[BindingSiteDomain.ligand_id, Domain.domain_id]",
                            uselist=True, innerjoin=True, lazy='dynamic',
                            backref=backref('BindingSites', uselist=True, lazy='dynamic',
                                            innerjoin=True))

    def __repr__(self):
        """
        """
        return '<BindingSite({self.ligand_id})>'.format(self=self)

    def pdbstring(self, **kwargs):
        """
        Returns the binding site environment of the ligand as PDB string.

        :param biomolecule_id: The biomolecule_id of the assembly that this
                               binding site is part of - required to pick the
                               right atom partition table. The biomolecule_id
                               of the parent ligand will be used if missing.
        """
        biomolecule_id = kwargs.get('biomolecule_id', self.Ligand.biomolecule_id)

        fn = func.credo.binding_site_pdbstring(biomolecule_id, self.ligand_id)

        with closing(Session()) as session:
            return session.query(fn).scalar()

class BindingSiteDomain(Base):
    """
    Mapping between protein-ligand binding sites and the domains they consist of.
    """
    __tablename__ = 'credo.binding_site_domains'

    Domain = relationship("Domain",
                          primaryjoin="BindingSiteDomain.domain_id==Domain.domain_id",
                          foreign_keys="[Domain.domain_id]",  uselist=False,
                          innerjoin=True)

class BindingSiteFuzcav(Base):
    """
    """
    __tablename__ = 'credo.binding_site_fuzcav'

class BindingSiteResidue(Base):
    """
    This class represents a row from the mapping between ligands and the residues
    they interact with, including solvents and other ligands.
    """
    __tablename__ = 'credo.binding_site_residues'

    Peptide = relationship("Peptide",
                           primaryjoin="Peptide.residue_id==BindingSiteResidue.residue_id",
                           foreign_keys="[Peptide.residue_id]",
                           uselist=False, innerjoin=True)

    Residue = relationship("Residue",
                           primaryjoin="and_(Residue.residue_id==BindingSiteResidue.residue_id, Residue.entity_type_bm==BindingSiteResidue.entity_type_bm)",
                           foreign_keys="[Residue.residue_id, Residue.entity_type_bm]",
                           uselist=False, innerjoin=True)

    Domain = relationship("Domain",
                          secondary=Base.metadata.tables['credo.domain_peptides'],
                          primaryjoin="BindingSiteResidue.residue_id==DomainPeptide.residue_id",
                          secondaryjoin="DomainPeptide.domain_id==Domain.domain_id",
                          foreign_keys="[DomainPeptide.residue_id, Domain.domain_id]",
                          uselist=False, innerjoin=True)

class BindingSiteAtomSurfaceArea(Base):
    """
    """
    __tablename__ = 'credo.binding_site_atom_surface_areas'
