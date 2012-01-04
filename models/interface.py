from sqlalchemy.orm import relationship

from credoscript import Base
from credoscript.mixins import PathMixin

class Interface(Base, PathMixin):
    '''
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
    '''
    __tablename__ = 'credo.interfaces'    
    
    ChainBgn = relationship("Chain",
                            primaryjoin="Chain.chain_id==Interface.chain_bgn_id",
                            foreign_keys="[Chain.chain_id]", uselist=False, innerjoin=True)
    
    ChainEnd = relationship("Chain",
                            primaryjoin="Chain.chain_id==Interface.chain_end_id",
                            foreign_keys="[Chain.chain_id]", uselist=False, innerjoin=True)    
    
    def __repr__(self):
        '''
        '''
        return '<Interface({self.chain_bgn_id} {self.chain_end_id})>'.format(self=self)

    def get_residues(self, *expressions):
        '''
        '''
        return ResidueAdaptor().fetch_all_by_interface_id(self.interface_id, *expressions)

    def get_contacts(self, *expressions):
        '''
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
        '''
        return ContactAdaptor().fetch_all_by_interface_id(self.interface_id,
                                                          Contact.biomolecule_id==self.biomolecule_id,
                                                          *expressions)

    def get_proximal_water(self, *expressions):
        '''
        Returns all water atoms that are in between the interface.

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
        '''
        return AtomAdaptor().fetch_all_water_by_interface_id(self.interface_id, *expressions)

from .contact import Contact
from ..adaptors.residueadaptor import ResidueAdaptor
from ..adaptors.atomadaptor import AtomAdaptor
from ..adaptors.contactadaptor import ContactAdaptor