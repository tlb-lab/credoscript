from sqlalchemy import select
from sqlalchemy.orm import backref, relationship, column_property
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import association_proxy

from credoscript import Base, schema

class LigandFragment(Base):
    """
    """
    __tablename__ = '%s.ligand_fragments' % schema['credo']

    Fragment = relationship("Fragment",
                            primaryjoin="Fragment.fragment_id==LigandFragment.fragment_id",
                            foreign_keys="[Fragment.fragment_id]",
                            uselist=False, innerjoin=True, 
                            backref=backref('LigandFragments', uselist=True))
                            
    #Ligand = backreffed from Ligand

    Atoms = relationship("Atom",
                         secondary=Base.metadata.tables['%s.ligand_fragment_atoms' % schema['credo']],
                         primaryjoin="and_(LigandFragment.ligand_fragment_id==LigandFragmentAtom.ligand_fragment_id, "
                                          "LigandFragment.ligand_id==LigandFragmentAtom.ligand_id)",
                         secondaryjoin="LigandFragmentAtom.atom_id==Atom.atom_id",
                         foreign_keys="[LigandFragmentAtom.ligand_fragment_id, LigandFragmentAtom.atom_id]",
                         uselist=True, lazy='dynamic')

    Contacts = relationship("Contact",
                            secondary=Base.metadata.tables['%s.ligand_fragment_atoms' % schema['credo']],
                            primaryjoin="and_(LigandFragment.ligand_fragment_id==LigandFragmentAtom.ligand_fragment_id, "
                                             "LigandFragment.ligand_id==LigandFragmentAtom.ligand_id)",
                            secondaryjoin="and_(or_(LigandFragmentAtom.atom_id==Contact.atom_bgn_id, LigandFragmentAtom.atom_id==Contact.atom_end_id), "
                                                "Contact.biomolecule_id==LigandFragment.biomolecule_id)",
                            foreign_keys="[LigandFragmentAtom.ligand_fragment_id, Contact.atom_bgn_id, Contact.atom_end_id, Contact.biomolecule_id]",
                            uselist=True, lazy='dynamic')

    ism = association_proxy('Fragment', 'ism')

    @hybrid_property
    def pdb_chain_id(self):
        return self.Ligand.pdb_chain_id

    @hybrid_property
    def ligand_name(self):
        return self.Ligand.ligand_name

    @hybrid_property
    def res_num(self):
        return self.Ligand.res_num

    @hybrid_property
    def path(self):
        return self.Ligand.path


    def __repr__(self):
        """
        """
        return '<LigandFragment({self.ligand_fragment_id})>'.format(self=self)

    def __iter__(self):
        """
        """
        return self.Atoms.all()

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
        adaptor = AtomAdaptor(dynamic=True)
        return adaptor.fetch_all_in_contact_with_ligand_fragment_id(self.ligand_fragment_id,
                                                                    self.biomolecule_id)

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
        adaptor = ResidueAdaptor(dynamic=True)
        return adaptor.fetch_all_in_contact_with_ligand_fragment_id(self.ligand_fragment_id,
                                                                    self.biomolecule_id)

    @property
    def atom_names(self):
        return [a.atom_name for a in self.Atoms]


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
