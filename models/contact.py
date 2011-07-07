from .model import Model

class Contact(Model):
    '''
    Represents a Contact entity from CREDO

    Attributes
    ----------
    contact_id : int
        Primary key.
    '''
    def __repr__(self):
        '''
        '''
        return "<Contact(%i, %i)>" % (self.atom_bgn_id, self.atom_end_id)

    @property
    def sift(self):
        '''
        '''
        return (self.is_covalent, self.is_vdw_clash, self.is_vdw, self.is_proximal,
                self.is_hbond, self.is_weak_hbond, self.is_xbond, self.is_ionic,
                self.is_metal_complex, self.is_aromatic, self.is_hydrophobic,
                self.is_carbonyl)