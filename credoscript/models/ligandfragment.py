from sqlalchemy.orm import backref, relationship

from credoscript import Base, Session, ligand_fcd

class LigandFragment(Base):
    """
    """
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

    Contacts = relationship("Contact",
                            secondary=Base.metadata.tables['credo.ligand_fragment_atoms'],
                            primaryjoin="LigandFragment.ligand_fragment_id==LigandFragmentAtom.ligand_fragment_id",
                            secondaryjoin="and_(or_(LigandFragmentAtom.atom_id==Contact.atom_bgn_id, LigandFragmentAtom.atom_id==Contact.atom_end_id), Contact.biomolecule_id==LigandFragment.biomolecule_id)",
                            foreign_keys="[LigandFragmentAtom.ligand_fragment_id, Contact.atom_bgn_id, Contact.atom_end_id, Contact.biomolecule_id]",
                            uselist=True, innerjoin=True, lazy='dynamic')

    def __repr__(self):
        """
        """
        return '<LigandFragment({self.ligand_fragment_id})>'.format(self=self)

    def __iter__(self):
        """
        """
        return self.Atoms.all()

    @property
    def fcd(self):
        """
        Returns the fragment contact density (FCD) for this ligand fragment.
        """
        session = Session()

        query = session.query(ligand_fcd.c.fcd)
        query = query.filter(ligand_fcd.c.ligand_fragment_id==self.ligand_fragment_id)

        fcd = query.scalar()

        session.close()

        return fcd

    @property
    def ProximalAtoms(self):
        """
        Returns all atoms that are in contact with this ligand fragment.

        Parameters
        ----------
        *expr : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried Entities
        ----------------
        Atom, Contact, ligand_fragment_atoms

        Returns
        -------
        atoms : list
            List of `Atom` objects.
        """
        return AtomAdaptor().fetch_all_in_contact_with_ligand_fragment_id(self.ligand_fragment_id,
                                                                          self.biomolecule_id,
                                                                          dynamic=True)

    @property
    def ProximalResidues(self):
        """
        Returns all residues that are in contact with the ligand fragment having
        the specified ligand fragment identifier.

        Parameters
        ----------
        *expr : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried Entities
        ----------------
        Residue

        Returns
        -------
        residues : list
            List of `Residue` objects.
        """
        return ResidueAdaptor().fetch_all_in_contact_with_ligand_fragment_id(self.ligand_fragment_id,
                                                                             self.biomolecule_id,
                                                                             dynamic=True)

    def sift(self, *expr, **kwargs):
        """
        Queried Entities
        ----------------
        Contact, Atom
        """
        return SIFtAdaptor().fetch_by_ligand_fragment_id(self.ligand_id,
                                                         self.biomolecule_id,
                                                         *expr)

from ..adaptors.atomadaptor import AtomAdaptor
from ..adaptors.residueadaptor import ResidueAdaptor
from ..adaptors.siftadaptor import SIFtAdaptor
