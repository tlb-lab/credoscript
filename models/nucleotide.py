from sqlalchemy.orm import backref, relationship

from credoscript import Base
from credoscript.mixins import PathMixin, ResidueMixin

class Nucleotide(Base, PathMixin, ResidueMixin):
    '''
    '''
    __tablename__ = 'credo.nucleotides'
    
    Residue = relationship("Residue",
                           primaryjoin="Residue.residue_id==Nucleotide.residue_id",
                           foreign_keys="[Residue.residue_id]", uselist=False, innerjoin=True,
                           backref=backref('Nucleotide', uselist=False, innerjoin=True))