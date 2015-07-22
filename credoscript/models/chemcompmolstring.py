from sqlalchemy.orm import deferred

from credoscript import Base, schema

class ChemCompMolString(Base):
    '''
    '''
    __table__ = Base.metadata.tables['%s.chem_comp_structures' % schema['pdbchem']]
    
    # DEFERRED COLUMNS  
    sdf = deferred(__table__.c.sdf)
    pdb = deferred(__table__.c.pdb)
    oeb = deferred(__table__.c.oeb)   