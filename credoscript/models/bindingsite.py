from contextlib import closing

from sqlalchemy import func
from credoscript import Base, Session

class BindingSite(Base):
    """
    """
    __tablename__ = 'credo.binding_sites'

    def pdbstring(self, **kwargs):
        """
        Returns the binding site environment of the ligand as PDB string.

        :param biomolecule_id: The biomolecule_id of the assembly that this
                               binding site is part of - required to pick the
                               right atom partition table. The biomolecule_id
                               of the parent ligand will be used if missing.
        """
        biomolecule_id = kwargs.get('biomolecule_id', self.Ligand.biomolecule_id)

        fn = func.credo.binding_site_pdbstring(biomolecule_id, self.ligand_id)

        with closing(Session()) as session:
            return session.query(fn).scalar()
