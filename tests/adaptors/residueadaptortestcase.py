from credoscript import adaptors, models
from tests import CredoAdaptorTestCase

class ResidueAdaptorTestCase(CredoAdaptorTestCase):
    def setUp(self):
        self.adaptor = adaptors.ResidueAdaptor()
        self.expected_entity = models.Residue

    def test_fetch_by_residue_id(self):
        """Fetch a single residue by residue_id"""
        self.assertSingleResult('fetch_by_residue_id', 1)

    def test_fetch_all_by_chain_id(self):
        """Fetch all residues that comprise a chain by chain_id"""
        self.assertPaginatedResult('fetch_all_by_chain_id', 123)

    def test_fetch_all_by_biomolecule_id(self):
        """Fetch all residues that comprise a biomolecule by biomolecule_id"""
        self.assertPaginatedResult('fetch_all_by_biomolecule_id', 123)

    def test_fetch_all_by_ligand_id(self):
        """Fetch all residues that comprise a ligand ligand_id"""
        self.assertPaginatedResult('fetch_all_by_ligand_id', 123)

    def test_fetch_all_in_contact_with_residue_id(self):
        """Fetch all residues that are in contact with the Residue having the
        specified residue_id."""
        self.assertPaginatedResult('fetch_all_in_contact_with_residue_id', 123)

    def test_fetch_all_in_contact_with_ligand_id(self):
        """Fetch all residues that are in contact with the ligand having the
        specified ligand_id."""
        self.assertPaginatedResult('fetch_all_in_contact_with_ligand_id', 123)

    def test_fetch_all_in_contact_with_ligand_fragment_id(self):
        """Returns all residues that are in contact with the ligand fragment having the specified
        identifier"""
        ligand = models.Ligand.query.filter_by(ligand_name='STI').first()
        lf = ligand.LigandFragments.first()

        self.assertPaginatedResult('fetch_all_in_contact_with_ligand_fragment_id',
                                   lf.ligand_fragment_id, ligand.biomolecule_id)

    def test_fetch_all_by_path_match(self):
        """retrieve ligands through ptree path match"""
        self.assertPaginatedResult('fetch_all_by_path_match', '2P33/0/*')

    def test_fetch_all_path_descendants(self):
        """retrieve ligands through ptree path descendants"""
        self.assertPaginatedResult('fetch_all_path_descendants', '2P33/0')