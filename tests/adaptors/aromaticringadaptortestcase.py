from credoscript import adaptors, models
from tests import CredoAdaptorTestCase

class AromaticRingAdaptorTestCase(CredoAdaptorTestCase):
    def setUp(self):
        self.adaptor = adaptors.AromaticRingAdaptor()
        self.expected_entity = models.AromaticRing

    def test_fetch_by_aromatic_ring_id(self):
        """Fetch a single aromatic ring by aromatic_ring_id"""
        self.assertSingleResult('fetch_by_aromatic_ring_id', 1)

    def test_fetch_all_by_biomolecule_id(self):
        """Fetch aromatic rings by biomolecule_id"""
        self.assertPaginatedResult('fetch_all_by_biomolecule_id', 1)

    def test_fetch_all_by_ligand_id(self):
        """Fetch aromatic rings by ligand_id"""
        ligand = models.Ligand.query.filter_by(ligand_name='STI').first()
        self.assertPaginatedResult('fetch_all_by_ligand_id', ligand.ligand_id)