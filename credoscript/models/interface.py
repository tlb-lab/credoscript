from sqlalchemy.orm import backref, relationship

from credoscript import Base, schema
from credoscript.mixins import PathMixin

class Interface(Base, PathMixin):
    """
    Represents the binary interaction between two polypeptide chains.

    Attributes
    ----------
    interface_id : int
        Primary key.
    biomolecule_id : int
        Primary key of the parent biomolecule.
    chain_bgn_id : int
        CREDO chain_id of the first Chain.
    chain_end_id : int
        CREDO chain_id of the second Chain.
    num_residues_bgn : int
        Number of residues of the first chain that are involved in the interaction.
    num_residues_end : int
        Number of residues of the second chain that are involved in the interaction.
    has_mod_res : boolean
        True if the interface has at least one modified residue.

    Mapped Attributes
    -----------------
    Biomolecule : Biomolecule
        Parent Biomolecule this is Interface comes from.
    ChainBgn : Chain
        First Chain of the Interface.
    ChainEnd : Chain
        Second Chain of the Interface.

    See Also
    --------
    InterfaceAdaptor : Fetch Interfaces from the database.
    """
    __tablename__ = '%s.interfaces' % schema['credo']

    ChainBgn = relationship("Chain",
                            primaryjoin="Chain.chain_id==Interface.chain_bgn_id",
                            foreign_keys="[Chain.chain_id]", uselist=False,
                            innerjoin=True)

    ChainEnd = relationship("Chain",
                            primaryjoin="Chain.chain_id==Interface.chain_end_id",
                            foreign_keys="[Chain.chain_id]", uselist=False,
                            innerjoin=True)

    Peptides = relationship("Peptide",
                            secondary=Base.metadata.tables['%s.interface_peptide_pairs' % schema['credo']],
                            primaryjoin="Interface.interface_id==InterfacePeptidePair.interface_id",
                            secondaryjoin="or_(InterfacePeptidePair.residue_bgn_id==Peptide.residue_id, InterfacePeptidePair.residue_end_id==Peptide.residue_id)",
                            foreign_keys="[InterfacePeptidePair.interface_id, Peptide.residue_id]",
                            uselist=True, innerjoin=True, lazy='dynamic')

    def __repr__(self):
        """
        """
        return '<Interface({self.path})>'.format(self=self)

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
        >>> ContactAdaptor().fetch_all_by_interface_id(1)
        <Contact()>
        """
        adaptor = ContactAdaptor(dynamic=True)
        return adaptor.fetch_all_by_interface_id(self.interface_id,
                                                 self.biomolecule_id)

    @property
    def ProximalWater(self):
        """
        Returns all water atoms that are between the interface.

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
        """
        adaptor = AtomAdaptor(dynamic=True)
        return adaptor.fetch_all_water_in_contact_with_interface_id(self.interface_id,
                                                                    self.biomolecule_id)

class InterfacePeptidePair(Base):
    """
    Mapping between interfaces and the interacting peptides of the participating
    polypeptide chains.
    """
    __tablename__ = '%s.interface_peptide_pairs' % schema['credo']

    Interface = relationship("Interface",
                             primaryjoin="InterfacePeptidePair.interface_id==Interface.interface_id",
                             foreign_keys="[InterfacePeptidePair.interface_id]",
                             uselist=False, innerjoin=True,
                             backref=backref('InterfacePeptidePairs', uselist=True,
                                             innerjoin=True, lazy='dynamic'))

    Peptides = relationship("Peptide",
                            primaryjoin="or_(InterfacePeptidePair.residue_bgn_id==Peptide.residue_id, InterfacePeptidePair.residue_end_id==Peptide.residue_id)",
                            foreign_keys="[Peptide.residue_id]",
                            uselist=True, innerjoin=True, lazy='dynamic')

    Domains = relationship("Domain",
                           secondary=Base.metadata.tables['%s.domain_peptides' % schema['credo']],
                           primaryjoin="or_(InterfacePeptidePair.residue_bgn_id==DomainPeptide.residue_id, InterfacePeptidePair.residue_end_id==DomainPeptide.residue_id)",
                           secondaryjoin="DomainPeptide.domain_id==Domain.domain_id",
                           foreign_keys="[DomainPeptide.residue_id, Domain.domain_id]",
                           uselist=True, innerjoin=True, lazy='dynamic')

    def __repr__(self):
        """
        """
        return '<InterfacePeptidePair({self.interface_id} {self.residue_bgn_id} {self.residue_end_id})>'.format(self=self)

from ..adaptors.residueadaptor import ResidueAdaptor
from ..adaptors.atomadaptor import AtomAdaptor
from ..adaptors.contactadaptor import ContactAdaptor
