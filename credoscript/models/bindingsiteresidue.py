from sqlalchemy.orm import backref, relationship
from credoscript import Base

class BindingSiteResidue(Base):
    '''
    '''
    __tablename__ = 'credo.binding_site_residues'

    Residue = relationship("Residue",
                           primaryjoin = "Residue.residue_id==BindingSiteResidue.residue_id",
                           foreign_keys = "[Residue.residue_id]",
                           uselist=False, innerjoin=True)