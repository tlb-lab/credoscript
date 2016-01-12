from sqlalchemy import Column
from sqlalchemy.orm import deferred

from credoscript import Base, schema
from credoscript.ext.rdkit_ import RDMol

_lms_table = Base.metadata.tables['%s.ligand_molstrings' % schema['credo']]

class LigandMolString(Base):
    """
    """
    __tablename__ = '%s.ligand_molstrings' % schema['credo']
    __table_args__ = {'autoload': True, 'extend_existing': True}

    # deferred columns
    pdb = deferred(Column('pdb', _lms_table.c.pdb.type))
    sdf = deferred(Column('sdf', _lms_table.c.sdf.type))
    oeb = deferred(Column('oeb', _lms_table.c.oeb.type))
    rdk = deferred(Column('rdk', RDMol()))

    def __repr__(self):
        """
        """
        return '<LigandMolString({self.ligand_id})>'.format(self=self)