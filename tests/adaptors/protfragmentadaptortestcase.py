from credoscript import adaptors, models
from tests import CredoAdaptorTestCase

class ProtFragmentAdaptorTestCase(CredoAdaptorTestCase):
    def setUp(self):
        self.adaptor = adaptors.ProtFragmentAdaptor()
        self.expected_entity = models.ProtFragment

    def test_fetch_by_prot_fragment_id(self):
        """Fetch a single protein fragment by protein_fragment_id"""
        self.assertSingleResult('fetch_by_prot_fragment_id', 1)

    def test_fetch_all_by_biomolecule_id(self):
        """Fetch protein fragments by biomolecule_id"""
        self.assertPaginatedResult('fetch_all_by_biomolecule_id', 1)

    def test_fetch_all_by_fragment_seq(self):
        """Fetch protein fragments by biomolecule_id"""
        fragment = models.ProtFragment.query.get(3)
        self.assertPaginatedResult('fetch_all_by_fragment_seq', fragment.fragment_seq)

    def test_fetch_all_by_pdb(self):
        """Fetch protein fragments by biomolecule_id"""
        self.assertPaginatedResult('fetch_all_by_pdb', '2P33')

    def test_fetch_all_in_contact_with_ligand_id(self):
        """Fetch protein fragments by biomolecule_id"""
        ligand = models.Ligand.query.filter_by(ligand_name='STI').first()
        self.assertPaginatedResult('fetch_all_in_contact_with_ligand_id', ligand.ligand_id)

    def test_fetch_all_by_path_match(self):
        """retrieve protein fragments through ptree path match"""
        self.assertPaginatedResult('fetch_all_by_path_match', '2P33/0/*')

    def test_fetch_all_path_descendants(self):
        """retrieve protein fragments through ptree path descendants"""
        self.assertPaginatedResult('fetch_all_path_descendants', '2P33/0')