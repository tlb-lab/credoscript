from sqlalchemy.orm import deferred

from credoscript import Base

class LigandMolString(Base):
    """
    """
    __table__ = Base.metadata.tables['credo.ligand_molstrings']

    # deferred columns
    pdb = deferred(__table__.c.pdb)
    oeb = deferred(__table__.c.oeb)

    def __repr__(self):
        """
        """
        return '<LigandMolString({self.ligand_id})>'.format(self=self)