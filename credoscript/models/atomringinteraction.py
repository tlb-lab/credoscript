from sqlalchemy.orm import backref, relationship

from credoscript import Base, schema

class AtomRingInteraction(Base):
    '''
    '''
    __tablename__ = '%s.atom_ring_interactions' % schema['credo']

    Atom = relationship("Atom",
                        primaryjoin="Atom.atom_id==AtomRingInteraction.atom_id",
                        foreign_keys="[Atom.atom_id]", uselist=False, innerjoin=True)

    AromaticRing = relationship("AromaticRing",
                                primaryjoin="AromaticRing.aromatic_ring_id==AtomRingInteraction.aromatic_ring_id",
                                foreign_keys="[AromaticRing.aromatic_ring_id]",
                                uselist=False, innerjoin=True,
                                backref=backref('AtomRingInteractions',
                                                uselist=True, innerjoin=True, lazy='dynamic'))

    def __repr__(self):
        '''
        '''
        return '<AtomRingInteraction({self.atom_ring_interaction_id})>'.format(self=self)


    def get_imz_str(self, mol_name=None):
        '''
        '''
        if mol_name is True:
            atom_path = self.Atom.pymolstring
        elif not mol_name:
            atom_path = '/'.join(self.Atom.path.split('/')[2:])
        else:
            path_toks = self.Atom.path.split('/')
            path_toks[0], path_toks[1] = mol_name, ''
            atom_path = '/'.join(path_toks)

        ring = self.AromaticRing
        path_toks = ring.path.split('/')
        name_concat = '+'.join(at.atom_name for at in ring.Atoms)

        s = 0
        if not mol_name:
            s = 2
        elif isinstance(mol_name, basestring):
            path_toks[0] = mol_name
        path_toks[1] = ''

        ring_field = "{} ({}) [{}]".format('/'.join(path_toks[s:-1] + [name_concat]),
                                           ' '.join('%.3f' % e for e in ring.centroid),
                                           ' '.join('%.3f' % e for e in ring.normal))

        return '\t'.join([atom_path, ring_field, self.interaction_type or ''])