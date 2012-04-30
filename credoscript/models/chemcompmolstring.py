from sqlalchemy.orm import deferred

from credoscript import Base

class ChemCompMolString(Base):
    '''
    '''
    __table__ = Base.metadata.tables['pdbchem.chem_comp_structures']
    
    # DEFERRED COLUMNS  
    sdf = deferred(__table__.c.sdf)
    pdb = deferred(__table__.c.pdb)
    oeb = deferred(__table__.c.oeb)   