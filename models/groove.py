from .model import Model

class Groove(Model):
    '''
    '''
    def __repr__(self):
        '''
        '''
        return '<Groove({self.chain_prot_id} {self.chain_nuc_id})>'.format(self=self)
    
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

        '''
        return ContactAdaptor().fetch_all_by_groove_id(self.groove_id,
                                                       Contact.biomolecule_id==self.biomolecule_id,
                                                       *expressions)

from .contact import Contact
from ..adaptors.contactadaptor import ContactAdaptor