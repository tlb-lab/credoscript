class LigandMatch(object):
    """
    This class is used to hold a ligand pattern match (substructure, SMARTS) and
    implements convenience attributes and methods to obtain contacts for a specific
    match, for example.
    """
    def __init__(self, pattern, ligand_id, biomolecule_id, ism, atom_names):
        self.ligand_id = ligand_id
        self.biomolecule_id = biomolecule_id
        self.ism = ism
        self.pattern = pattern
        self.atom_names = atom_names

    def __repr__(self):
        return '<LigandMatch({self.ligand_id}, {self.pattern})>'.format(self=self)

    @property
    def Ligand(self):
        """
        Returns the ligand of this match.
        """
        return Ligand.query.get(self.ligand_id)

    @property
    def Hetatms(self):
        """
        Returns the atoms of the ligand that match the pattern.
        """
        adaptor = AtomAdaptor(dynamic=True)
        return adaptor.fetch_all_by_ligand_id_and_atom_names(self.ligand_id,
                                                             self.biomolecule_id,
                                                             self.atom_names)

    @property
    def Contacts(self):
        """
        Returns the contacts of the ligand atoms that match the initial pattern.
        """
        adaptor = ContactAdaptor(dynamic=True)
        return adaptor.fetch_all_by_ligand_id_and_atom_names(self.ligand_id,
                                                             self.biomolecule_id,
                                                             self.atom_names)

    @property
    def ProximalResidues(self):
        """
        Returns the residues that are in contact with this ligand match.
        """
        adaptor = ResidueAdaptor(dynamic=True)
        return adaptor.fetch_all_in_contact_with_ligand_id_and_atom_names(self.ligand_id,
                                                                          self.biomolecule_id,
                                                                          self.atom_names)

    def sift(self, *expr):
        """
        Returns the Structural Interaction Fingerprint for the atoms that match
        the chemical pattern.

        Queried Entities
        ----------------
        Contact, Atom, MatchAtom (Atom), Hetatm
        """
        return SIFtAdaptor().fetch_by_ligand_id_and_atom_names(self.ligand_id,
                                                               self.biomolecule_id,
                                                               self.atom_names,
                                                               *expr)

from .ligand import Ligand
from ..adaptors.residueadaptor import ResidueAdaptor
from ..adaptors.atomadaptor import AtomAdaptor
from ..adaptors.contactadaptor import ContactAdaptor
from ..adaptors.siftadaptor import SIFtAdaptor