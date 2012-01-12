from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql.expression import func

from credoscript import Base, session

class LigandFragment(Base):
    '''
    '''
    __tablename__ = 'credo.ligand_fragments'    
    
    Fragment = relationship("Fragment",
                            primaryjoin="Fragment.fragment_id==LigandFragment.fragment_id",
                            foreign_keys="[Fragment.fragment_id]",
                            uselist=False, innerjoin=True,
                            backref=backref('LigandFragments',uselist=True, innerjoin=True))
    
    Atoms = relationship("Atom",
                         secondary=Base.metadata.tables['credo.ligand_fragment_atoms'],
                         primaryjoin="LigandFragment.ligand_fragment_id==LigandFragmentAtom.ligand_fragment_id",
                         secondaryjoin="LigandFragmentAtom.atom_id==Atom.atom_id",
                         foreign_keys="[LigandFragmentAtom.ligand_fragment_id, LigandFragmentAtom.atom_id]",
                         uselist=True, innerjoin=True, lazy='dynamic') 
    
    def __repr__(self):
        '''
        '''
        return '<LigandFragment({self.ligand_fragment_id})>'.format(self=self)

    def __iter__(self):
        '''
        '''
        return self.Atoms

    def get_contacting_atoms(self, *expressions):
        '''
        Returns all atoms that are in contact with this ligand fragment.

        Parameters
        ----------
        *expressions : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried Entities
        ----------------
        Atom, Contact, ligand_fragment_atoms

        Returns
        -------
        atoms : list
            List of `Atom` objects.
        '''
        return AtomAdaptor().fetch_all_in_contact_with_ligand_fragment_id(self.ligand_fragment_id, *expressions)

    def get_contacting_residues(self, *expressions):
        '''
        Returns all residues that are in contact with the ligand fragment having
        the specified ligand fragment identifier.

        Parameters
        ----------
        *expressions : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried Entities
        ----------------
        Residue

        Returns
        -------
        residues : list
            List of `Residue` objects.
        '''
        return ResidueAdaptor().fetch_all_in_contact_with_ligand_fragment_id(self.ligand_fragment_id, *expressions)

    def usrenv(self, *args, **kwargs):
        '''
        '''
        # FACTOR BY WHICH THE USR SHAPE MOMENTS WILL BE ENLARGED IN USER SPACE
        probe_radius = kwargs.get('probe_radius', 0.5)

        # MAXIMUM NUMBER OF CHEMICAL COMPONENTS TO BE RETURNED
        limit = kwargs.get('limit', 25)

        # WEIGHTS FOR THE INDIVIDUAL ATOM TYPE MOMENTS
        hw = kwargs.get('hw', 0.2)
        rw = kwargs.get('rw', 0.2)
        aw = kwargs.get('aw', 0.2)
        dw = kwargs.get('dw', 0.2)

        # CREATE A PROBE AROUND THE QUERY IN USR SPACE IF NONE IS PROVIDED
        probe = func.cube_enlarge(self.usr_space, probe_radius, 12).label('probe')

        # CALCULATE USRCAT SIMILARITY FOR THE TOP HITS IN SEARCH SPACE
        similarity = func.usrsim(LigandFragment.usr_moments_env, self.usr_moments_env, hw, rw, aw, dw).label('similarity')

        # GET ALL HITS THAT ARE CONTAINED WITHIN THE ENLARGED SPACE
        query = session.query(LigandFragment, similarity).filter(LigandFragment.usr_space.op('<@')(probe))

        # SORT BY CUBE DISTANCE AND ONLY KEEP THE TOP 1000 HITS IN USR SPACE
        query = query.order_by('similarity DESC').limit(limit)

        return query.all()

from ..adaptors.atomadaptor import AtomAdaptor
from ..adaptors.residueadaptor import ResidueAdaptor