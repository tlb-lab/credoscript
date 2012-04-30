from credoscript import adaptors, models
from tests import CredoAdaptorTestCase

class BiomoleculeAdaptorTestCase(CredoAdaptorTestCase):
    def setUp(self):
        self.adaptor = adaptors.BiomoleculeAdaptor()
        self.expected_entity = models.Biomolecule

    def test_fetch_by_biomolecule_id(self):
        """Fetch a single biomolecule by biomolecule_id"""
        self.assertSingleResult('fetch_by_biomolecule_id', 1)

    def test_fetch_all_by_pdb(self):
        """Fetch all biomolecules that are part of a PDB entry"""
        self.assertPaginatedResult('fetch_all_by_pdb', '2P33')