from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import or_
from sqlalchemy.ext.hybrid import hybrid_method

from credoscript import Base, schema
from credoscript.mixins import PathMixin

class LigLigInteraction(Base, PathMixin):
    """
    Represents a ligand-ligand interaction from CREDO.
    """
    __tablename__ = '%s.lig_lig_interactions' % schema['credo']

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

    @hybrid_method
    @property
    def has_enzyme_cmpd(self):
        """
        Meta Boolean flag indicating whether one of the ligand in this interaction
        is the enzyme's substrate or product or not.
        """
        return any((self.has_product==True, self.has_substrate==True))

    @has_enzyme_cmpd.expression
    @property
    def has_enzyme_cmpd(self):
        """
        Returns an SQLAlchemy boolean clause list that enables usage of this
        meta LigLigInteraction flag to filter query constructs.
        """
        return or_(LigLigInteraction.has_product==True,
                   LigLigInteraction.has_substrate==True)