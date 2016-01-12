from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import func

from credoscript import Base, schema, Session, chem_comp_fragment_atoms

class ChemCompFragment(Base):
    """
    """
    __tablename__ = '%s.chem_comp_fragments' % schema['pdbchem']
    
    def __repr__(self):
        """
        """
        return '<ChemCompFragment({self.het_id} {self.fragment_id})>'.format(self=self)

    @property
    def pdb_atom_names(self):
        """
        """
        session = Session()
        
        query = session.query(chem_comp_fragment_atoms.c.hit, func.array_agg(chem_comp_fragment_atoms.c.pdb_name))
        query = query.filter(chem_comp_fragment_atoms.c.chem_comp_fragment_id==self.chem_comp_fragment_id)
        query = query.group_by(chem_comp_fragment_atoms.c.hit)

        return query.all()