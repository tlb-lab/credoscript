from credoscript import adaptors, models
from tests import CredoAdaptorTestCase

class RingInteractionAdaptorTestCase(CredoAdaptorTestCase):
    def setUp(self):
        self.adaptor = adaptors.RingInteractionAdaptor()
        self.expected_entity = models.RingInteraction

    def test_fetch_by_ring_interaction_id(self):
        """Fetch a single ring interaction by ring_interaction_id"""
        self.assertSingleResult('fetch_by_ring_interaction_id', 1)

    def test_fetch_all_by_aromatic_ring_id(self):
        """Fetch ring interactions by aromatic_ring_id"""
        ri = models.RingInteraction.query.get(1)
        self.assertPaginatedResult('fetch_all_by_aromatic_ring_id',
                                   ri.AromaticRingBgn.aromatic_ring_id)

    def test_fetch_all_by_ligand_id(self):
        """Fetch ring interactions by by ligand_id"""
        ligand = models.Ligand.query.filter_by(ligand_name='STI').first()
        self.assertPaginatedResult('fetch_all_by_ligand_id', ligand.ligand_id)
