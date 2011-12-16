from sqlalchemy.orm import backref, relationship
from sqlalchemy.orm.collections import attribute_mapped_collection

from credoscript import Base
from credoscript.mixins import PathMixin, ResidueMixin

class Peptide(Base, PathMixin, ResidueMixin):
    '''
    '''
    __tablename__ = 'credo.peptides'    
    
    Residue = relationship("Residue",
                            primaryjoin="Residue.residue_id==Peptide.residue_id",
                            foreign_keys="[Residue.residue_id]", uselist=False, innerjoin=True,
                            backref=backref('Peptide', uselist=False, innerjoin=True))
    
    ResMap = relationship("ResMap",
                          primaryjoin="ResMap.res_map_id==Peptide.res_map_id",
                          foreign_keys = "[ResMap.res_map_id]",
                          uselist=False, innerjoin=True)
    
    ProtFragment = relationship("ProtFragment",
                                secondary = Base.metadata.tables['credo.prot_fragment_residues'],
                                primaryjoin = "Peptide.residue_id==ProtFragmentResidue.residue_id",
                                secondaryjoin = "ProtFragmentResidue.prot_fragment_id==ProtFragment.prot_fragment_id",
                                foreign_keys = "[ProtFragmentResidue.residue_id, ProtFragmentResidue.prot_fragment_id]",
                                uselist=False, innerjoin=True,
                                backref = backref('Peptides', uselist=True, innerjoin=True))    