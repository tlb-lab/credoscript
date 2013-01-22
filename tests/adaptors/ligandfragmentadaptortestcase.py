from credoscript import adaptors, models
from tests import CredoAdaptorTestCase

class LigandFragmentAdaptorTestCase(CredoAdaptorTestCase):
    def setUp(self):
        self.adaptor = adaptors.LigandFragmentAdaptor()
        self.expected_entity = models.LigandFragment

    def test_fetch_by_ligand_fragment_id(self):
        """Fetch a single ligand fragment by ligand_fragment_id"""
        ligand_fragment = models.LigandFragment.query.limit(1).first()
        self.assertSingleResult('fetch_by_ligand_fragment_id', ligand_fragment.ligand_fragment_id)

    def test_fetch_all_by_ligand_id(self):
        """Fetch ligand fragments by ligand_id"""
        ligand = models.Ligand.query.limit(1).first()
        self.assertPaginatedResult('fetch_all_by_ligand_id', ligand.ligand_id)

    def test_fetch_all_having_xbonds(self):
        """Fetch ligand fragments that form halogen bonds"""
        self.assertPaginatedResult('fetch_all_having_xbonds')

    def test_fetch_all_having_metal_complexes(self):
        """Fetch ligand fragments that form metal complexes"""
        self.assertPaginatedResult('fetch_all_having_metal_complexes')
