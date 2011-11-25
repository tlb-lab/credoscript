from .model import Model

class Peptide(Model):
    '''
    '''
    def __repr__(self):
        '''
        '''
        return '<Peptide({self.residue_id})>'.format(self=self)

    def __getitem__(self, atom):
        '''
        '''
        # ONLY ATOM NAME IS PROVIDED / WILL TREAT ALTERNATE LOCATION AS BLANK
        if isinstance(atom, str): return self.Atoms.get((atom, ' '))

        # ALTERNATE LOCATION WAS PROVIDED AS WELL
        elif isinstance(atom, tuple): return self.Atoms.get(atom)

    def __iter__(self):
        '''
        '''
        return iter(self.Atoms.values())