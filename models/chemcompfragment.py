from sqlalchemy.sql.expression import func

from .model import Model
from ..meta import session, chem_comp_fragment_atoms

class ChemCompFragment(Model):
    '''
    '''
    def __repr__(self):
        '''
        '''
        return '<ChemCompFragment({self.het_id} {self.fragment_id})>'.format(self=self)

    def __getitem__(self):
        '''
        '''
        pass

    def __hash__(self):
        '''
        '''
        return self.chem_fragment_id

    def __eq__(self, other):
        '''
        '''
        return self.chem_fragment_id == other.chem_fragment_id

    def __ne__(self, other):
        '''
        '''
        return self.chem_fragment_id != other.chem_fragment_id

    @property
    def pdb_atom_names(self):
        '''
        '''
        query = session.query(chem_comp_fragment_atoms.c.hit, func.array_agg(chem_comp_fragment_atoms.c.pdb_name))
        query = query.filter(chem_comp_fragment_atoms.c.chem_comp_fragment_id==self.chem_comp_fragment_id)
        query = query.group_by(chem_comp_fragment_atoms.c.hit)

        return query.all()
