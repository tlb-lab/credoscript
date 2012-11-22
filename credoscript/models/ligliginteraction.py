from sqlalchemy.orm import relationship
from credoscript import Base

class LigLigInteraction(Base):
    """
    Represents a ligand-ligand interaction from CREDO.
    """
    __tablename__ = 'credo.lig_lig_interactions'

    LigandBgn = relationship("Ligand",
                             primaryjoin="Ligand.ligand_id==LigLigInteraction.lig_bgn_id",
                             foreign_keys="[Ligand.ligand_id]", uselist=False)

    LigandEnd = relationship("Ligand",
                             primaryjoin="Ligand.ligand_id==LigLigInteraction.lig_end_id",
                             foreign_keys="[Ligand.ligand_id]", uselist=False)

    Ligands = relationship("Ligand",
                            primaryjoin="or_(Ligand.ligand_id==LigLigInteraction.lig_bgn_id, Ligand.ligand_id==LigLigInteraction.lig_end_id)",
                            foreign_keys="[Ligand.ligand_id]", uselist=False)

    def __repr__(self):
        """
        """
        return '<LigLigInteraction({self.path})>'.format(self=self)