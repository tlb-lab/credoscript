from credoscript import adaptors, models
from tests import CredoAdaptorTestCase

class LigandAdaptorTestCase(CredoAdaptorTestCase):
    def setUp(self):
        self.adaptor = adaptors.LigandAdaptor()
        self.expected_entity = models.Ligand

    def test_fetch_by_ligand_id(self):
        """Fetch a single ligand by ligand_id"""
        self.assertSingleResult('fetch_by_ligand_id', 1)

    def test_fetch_all_by_structure_id(self):
        """Fetch ligands by structure_id"""
        self.assertPaginatedResult('fetch_all_by_structure_id', 1)

    def test_fetch_all_by_het_id(self):
        self.assertPaginatedResult('fetch_all_by_het_id', 'STI')

    def test_fetch_all_in_contact_with_residue_id(self):
        """Fetch ligands in contact with a binding site residue identifier"""
        peptide = models.Peptide.query.filter_by(path='2P33/0/A/SER`72').first()
        self.assertPaginatedResult('fetch_all_in_contact_with_residue_id',
                                   peptide.residue_id)

    def test_fetch_all_in_contact_with_chain_id(self):
        """Fetch ligands in contact with binding site residues by chain_id"""
        chain = models.Chain.query.filter_by(path='2P33/0/A').first()
        self.assertPaginatedResult('fetch_all_in_contact_with_chain_id',
                                   chain.chain_id)

    def test_fetch_all_by_phenotype_id(self):
        """Fetch ligands by variation phenotype_id"""
        self.assertPaginatedResult('fetch_all_by_phenotype_id', 169)

    def test_fetch_all_by_chembl_id(self):
        """Fetch all ligands by ChEMBL compound"""
        self.assertPaginatedResult('fetch_all_by_chembl_id', 'CHEMBL1323')

    def test_fetch_all_by_uniprot(self):
        """Fetch all ligands whose binding sites match a UniProt accession"""
        self.assertPaginatedResult('fetch_all_by_uniprot', 'P03372')

    def test_fetch_all_by_cath_dmn(self):
        self.assertPaginatedResult('fetch_all_by_cath_dmn', '1bcuH01')

    def test_fetch_all_by_usr_moments(self):
        """Fetch all ligands by USR moments"""
        self.adaptor.dynamic = True
        ligand = self.adaptor.fetch_all_by_het_id('STI').first()
        self.adaptor.dynamic = True

        # test with ligand_id / use binary expression to fake query argument
        self.assertPaginatedSimilarityHits('fetch_all_by_usr_moments',
                                           ligand_id=ligand.ligand_id)

    def test_fetch_all_by_path_match(self):
        """retrieve ligands through ptree path match"""
        self.assertPaginatedResult('fetch_all_by_path_match', '2P33/0/A/*')

    def test_fetch_all_path_descendants(self):
        """retrieve ligands through ptree path descendants"""
        self.assertPaginatedResult('fetch_all_path_descendants', '2P33/0')
