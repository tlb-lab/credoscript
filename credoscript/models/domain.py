from sqlalchemy.orm import backref, relationship
from credoscript import Base

class Domain(Base):
    """
    Represents a unique protein domain from CATH, Pfam or SCOP in CREDO. CATH
    and SCOP are usually linked to a single PDB chain whereas Pfam is not.
    """
    __tablename__ = 'credo.domains'

    Peptides = relationship("Peptide",
                            secondary=Base.metadata.tables['credo.domain_peptides'],
                            primaryjoin="Domain.domain_id==DomainPeptide.domain_id",
                            secondaryjoin="DomainPeptide.residue_id==Peptide.residue_id",
                            foreign_keys="[DomainPeptide.domain_id, Peptide.residue_id]",
                            uselist=True, innerjoin=True, lazy='dynamic',
                            backref=backref('DomainList', uselist=True))

    # all ligands that are in contact with this domain
    Ligands = relationship("Ligand",
                           secondary=Base.metadata.tables['credo.binding_site_domains'],
                           primaryjoin="Domain.domain_id==BindingSiteDomain.domain_id",
                           secondaryjoin="BindingSiteDomain.ligand_id==Ligand.ligand_id",
                           foreign_keys="[BindingSiteDomain.domain_id, Ligand.ligand_id]",
                           uselist=True, innerjoin=True, lazy='dynamic',
                           backref=backref('Domains', uselist=True, lazy='dynamic',
                                           innerjoin=True))

    def __repr__(self):
        """
        """
        return '<Domain({self.db_source} {self.db_accession_id})>'.format(self=self)

    @property
    def Chains(self):
        """
        Returns a query that will return all the chains that contain this domain.
        """
        adaptor = ChainAdaptor(dynamic=True)
        return adaptor.fetch_all_by_domain_id(self.domain_id)

class DomainPeptide(Base):
    """
    Mapping between domains and the peptides they consist of.
    """
    __tablename__ = 'credo.domain_peptides'

    Peptide = relationship("Peptide",
                           primaryjoin="DomainPeptide.residue_id==Peptide.residue_id",
                           foreign_keys="[Peptide.residue_id]",
                           uselist=False, innerjoin=True,
                           backref=backref('DomainPeptide', uselist=False, innerjoin=True))

    Domain = relationship("Domain",
                          primaryjoin="DomainPeptide.domain_id==Domain.domain_id",
                          foreign_keys="[Domain.domain_id]",
                          uselist=False, innerjoin=True,
                          backref=backref('DomainPeptides', uselist=True, lazy='dynamic',
                                          innerjoin=True))

    def __repr__(self):
        """
        """
        return '<DomainPeptide({self.domain_id} {self.residue_id})>'.format(self=self)

from ..adaptors.chainadaptor import ChainAdaptor