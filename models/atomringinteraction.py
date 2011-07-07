from .model import Model

class AtomRingInteraction(Model):
    '''
    '''
    def __repr__(self):
        '''
        '''
        return '<AtomRingInteraction({self.atom_ring_interaction_id})>'.format(self=self)

    def __hash__(self):
        '''
        '''
        return self.atom_ring_interaction_id

    def __eq__(self, other):
        '''
        '''
        return self.atom_ring_interaction_id == other.atom_ring_interaction_id

    def __ne__(self, other):
        '''
        '''
        return self.atom_ring_interaction_id != other.atom_ring_interaction_id