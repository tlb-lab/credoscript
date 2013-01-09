from credoscript import adaptors, models
from tests import CredoAdaptorTestCase

class LigNucInteractionAdaptorTestCase(CredoAdaptorTestCase):
    def setUp(self):
        self.adaptor = adaptors.LigNucInteractionAdaptor()
        self.expected_entity = models.LigNucInteraction

    def test_fetch_by_lig_lig_interaction_id(self):
        """Fetch a single Ligand-Ligand interaction by fetch_by_lig_nuc_interaction_id"""
        self.assertSingleResult('fetch_by_lig_nuc_interaction_id', 1)

    def test_fetch_all_by_biomolecule_id(self):
        """Fetch all ligand-nucleic acid interactions by biomolecule_id"""
        lignucint = models.LigNucInteraction.query.limit(1).first()
        self.assertPaginatedResult('fetch_all_by_biomolecule_id',
                                   lignucint.biomolecule_id)

    def test_fetch_all_by_ligand_id(self):
        """Fetch all ligand-nucleic acid interactions by ligand_id"""
        lignucint = models.LigNucInteraction.query.limit(1).first()
        self.assertPaginatedResult('fetch_all_by_ligand_id',
                                   lignucint.ligand_id)

    def test_fetch_all_by_het_id(self):
        """Fetch all ligand-nucleic acid interactions by HET-ID"""
        lignucint = models.LigNucInteraction.query.limit(1).first()
        self.assertPaginatedResult('fetch_all_by_het_id',
                                   lignucint.Ligand.ligand_name)

    def test_fetch_all_by_lig_min_hvy_atoms(self):
        """Fetch all ligand-nucleic acid interactions where the ligand has a minimum number of atoms"""
        self.assertPaginatedResult('fetch_all_by_lig_min_hvy_atoms', 7)

    def fetch_all_having_drug_like_ligands(self):
        """Fetch all ligand-nucleic acid interactions where the ligand is drug-like"""
        self.assertPaginatedResult('fetch_all_having_drug_like_ligands')

    def fetch_all_having_app_drugs(self):
        """Fetch all ligand-nucleic acid interactions where the ligand is an approved drug"""
        self.assertPaginatedResult('fetch_all_having_app_drugs')