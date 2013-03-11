from sqlalchemy.orm import backref, relationship

from credoscript import Base
from credoscript.mixins import PathMixin

class Groove(Base, PathMixin):
    """
    Class representing a Groove entity from CREDO. A groove is a binary interaction
    between a polypeptide and a oligonucleotide chain (DNA/RNA/Hybrid).

    Attributes
    ----------

    Mapped Attributes
    -----------------

    """
    __tablename__ = 'credo.grooves'

    ChainProt = relationship("Chain",
                             primaryjoin="Chain.chain_id==Groove.chain_prot_id",
                             foreign_keys="[Chain.chain_id]", uselist=False, innerjoin=True)

    ChainNuc = relationship("Chain",
                            primaryjoin="Chain.chain_id==Groove.chain_nuc_id",
                            foreign_keys="[Chain.chain_id]", uselist=False, innerjoin=True)
    
    Peptides = relationship("Peptide",
                            secondary=Base.metadata.tables['credo.groove_residue_pairs'],
                            primaryjoin="Groove.groove_id==GrooveResiduePair.groove_id",
                            secondaryjoin="GrooveResiduePair.residue_prot_id==Peptide.residue_id",
                            foreign_keys="[GrooveResiduePair.groove_id, Peptide.residue_id]",
                            uselist=True, innerjoin=True, lazy='dynamic')

    def __repr__(self):
        return '<Groove({self.path})>'.format(self=self)

    @property
    def Contacts(self):
        """
        Returns all the Contacts that are formed between the two Chains of this
        Interface.

        Parameters
        ----------
        *expressions : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried Entities
        ----------------
        Contact, AtomBgn (Atom), AtomEnd (Atom), ResidueBgn (Residue),
        ResidueEnd (Residue), Interface

        Returns
        -------
        contacts : list
            Contacts that are formed between the two Chains of this Interface.

         Examples
        --------

        """
        adaptor = ContactAdaptor(dynamic=True)
        return adaptor.fetch_all_by_groove_id(self.groove_id, self.biomolecule_id)

class GrooveResiduePair(Base):
    """
    """
    __tablename__ = 'credo.groove_residue_pairs'
    
    Groove = relationship("Groove",
                          primaryjoin="GrooveResiduePair.groove_id==Groove.groove_id",
                          foreign_keys="[Groove.groove_id]", uselist=False,
                          innerjoin=True,
                          backref=backref('GrooveResiduePairs', uselist=True,
                                          lazy='dynamic', innerjoin=True))

from ..adaptors.contactadaptor import ContactAdaptor
