from sqlalchemy.orm import relationship
from credoscript import Base

class Hetatm(Base):
    '''
    '''
    __tablename__ = 'credo.hetatms'
    
    Contacts  = relationship("Contact",
                             primaryjoin="or_(Contact.atom_bgn_id==Hetatm.atom_id, Contact.atom_end_id==Hetatm.atom_id)",
                             foreign_keys="[Contact.atom_bgn_id, Contact.atom_end_id]",
                             uselist=True, innerjoin=True, lazy='dynamic')