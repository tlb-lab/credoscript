from sqlalchemy.orm import relationship
from credoscript import Base

class BindingSiteResidue(Base):
    """
    This class represents a row from the mapping between ligands and the residues
    they interact with, including solvents and other ligands.
    """
    __tablename__ = 'credo.binding_site_residues'

    Residue = relationship("Residue",
                           primaryjoin="and_(Residue.residue_id==BindingSiteResidue.residue_id, Residue.entity_type_bm==BindingSiteResidue.entity_type_bm)",
                           foreign_keys="[Residue.residue_id, Residue.entity_type_bm]",
                           uselist=False, innerjoin=True)
