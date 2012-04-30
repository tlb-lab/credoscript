from sqlalchemy.orm import relationship

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

    def __repr__(self):
        return '<Groove({self.chain_prot_id} {self.chain_nuc_id})>'.format(self=self)

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
        return ContactAdaptor().fetch_all_by_groove_id(self.groove_id,
                                                       self.biomolecule_id,
                                                       dynamic=True)

from .contact import Contact
from ..adaptors.contactadaptor import ContactAdaptor