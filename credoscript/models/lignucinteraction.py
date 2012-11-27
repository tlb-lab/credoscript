from sqlalchemy.orm import relationship

from credoscript import Base
from credoscript.mixins import PathMixin

class LigNucInteraction(Base, PathMixin):
    """
    Represents a ligand-nucleic interaction from CREDO.
    """
    __tablename__ = 'credo.lig_nuc_interactions'

    Biomolecule = relationship("Biomolecule",
                               primaryjoin="Biomolecule.biomolecule_id==LigNucInteraction.biomolecule_id",
                               foreign_keys="[Biomolecule.biomolecule_id]", uselist=False)

    Ligand = relationship("Ligand",
                          primaryjoin="Ligand.ligand_id==LigNucInteraction.ligand_id",
                          foreign_keys="[Ligand.ligand_id]", uselist=False)

    Oligonucleotide = relationship("Chain",
                                   primaryjoin="Chain.chain_id==LigNucInteraction.chain_nuc_id",
                                   foreign_keys="[Chain.chain_id]", uselist=False)

    def __repr__(self):
        """
        """
        return '<LigNucInteraction({self.path})>'.format(self=self)