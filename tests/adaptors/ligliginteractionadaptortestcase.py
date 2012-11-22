from credoscript import adaptors, models
from tests import CredoAdaptorTestCase

class LigLigInteractionAdaptorTestCase(CredoAdaptorTestCase):
    def setUp(self):
        self.adaptor = adaptors.LigLigInteractionAdaptor()
        self.expected_entity = models.LigLigInteraction

    def test_fetch_by_lig_lig_interaction_id(self):
        """Fetch a single Ligand-Ligand interaction by fetch_by_lig_lig_interaction_id"""
        self.assertSingleResult('fetch_by_lig_lig_interaction_id', 1)

    def test_fetch_all_by_biomolecule_id(self):
        """Fetch all ligand-ligand interactions by biomolecule_id"""
        ligligint = models.LigLigInteraction.query.limit(1).first()
        self.assertPaginatedResult('fetch_all_by_biomolecule_id',
                                   ligligint.biomolecule_id)

    def test_fetch_all_by_ligand_id(self):
        """Fetch all ligand-ligand interactions by ligand_id"""
        ligligint = models.LigLigInteraction.query.limit(1).first()
        self.assertPaginatedResult('fetch_all_by_ligand_id',
                                   ligligint.lig_bgn_id)

    def test_fetch_all_by_het_id(self):
        """Fetch all ligand-ligand interactions by HET-ID"""
        ligligint = models.LigLigInteraction.query.limit(1).first()
        self.assertPaginatedResult('fetch_all_by_het_id',
                                   ligligint.LigandBgn.ligand_name)