from credoscript import adaptors, models
from tests import CredoAdaptorTestCase

class ChemCompAdaptorTestCase(CredoAdaptorTestCase):
    def setUp(self):
        self.adaptor = adaptors.ChemCompAdaptor()
        self.expected_entity = models.ChemComp

    def test_fetch_by_chem_comp_id(self):
        """Fetch a single chemical component by chem_comp_id"""
        self.assertSingleResult('fetch_by_chem_comp_id', 1)

    def test_fetch_by_het_id(self):
        """Fetch a single chemical component by het_id"""
        self.assertSingleResult('fetch_by_het_id', 'STI')

    def test_fetch_by_residue_id(self):
        """Fetch a single chemical component by residue_id"""
        self.assertSingleResult('fetch_by_residue_id', 123)

    def test_fetch_all_by_fragment_id(self):
        """Fetch all chemical components linked to a fragment_id"""
        self.assertPaginatedResult('fetch_all_by_fragment_id', 9162)

    def test_fetch_all_by_xref(self):
        """Fetch all chemical components linked to a cross reference"""
        self.assertPaginatedResult('fetch_all_by_xref', 'ChEMBL Compound', 'CHEMBL941')

    def test_fetch_all_by_chembl_id(self):
        """Fetch all chemical components linked to a ChEMBL compound"""
        self.assertPaginatedResult('fetch_all_by_chembl_id', 'CHEMBL941')

    def test_fetch_all_approved_drugs(self):
        """Fetch all chemical components that are approved drugs"""
        self.assertPaginatedResult('fetch_all_approved_drugs')

    def test_fetch_all_by_substruct(self):
        """Fetch all chemical components through substructure match"""
        self.assertPaginatedResult('fetch_all_by_substruct','c1cc(cnc1)c2ccncn2')

    def test_fetch_all_by_superstruct(self):
        """Fetch all chemical components through superstructure match"""
        self.assertPaginatedResult('fetch_all_by_substruct','C[NH+](C)CCCC(=O)Nc1ccc(cc1)C(=O)Nc2cccc(c2)Nc3nccc(n3)c4cccnc4')

    def test_fetch_all_by_smarts(self):
        """Fetch all chemical components through SMARTS match"""
        self.assertPaginatedResult('fetch_all_by_smarts','c1cc(cnc1)c2ccncn2')

    def test_fetch_all_by_sim(self):
        """Fetch all chemical components through chemical similarity using RDKit"""
        for fptype in ('circular','atompair','torsion'):
            self.assertPaginatedSimilarityHits('fetch_all_by_sim', 'C[NH+](C)CCCC(=O)Nc1ccc(cc1)C(=O)Nc2cccc(c2)Nc3nccc(n3)c4cccnc4', fp=fptype)

    def test_fetch_all_by_trgm_sim(self):
        """Fetch all chemical components through trigram similarity"""
        self.assertPaginatedSimilarityHits('fetch_all_by_trgm_sim', 'C[NH+](C)CCCC(=O)Nc1ccc(cc1)C(=O)Nc2cccc(c2)Nc3nccc(n3)c4cccnc4')

    def test_fetch_all_by_usr_moments(self):
        """Fetch all chemical components through a USR search"""
        chemcomp = self.adaptor.fetch_by_het_id('STI')
        conformer = chemcomp.Conformers.first()

        # test with ligand_id / use binary expression to fake query argument
        self.assertPaginatedSimilarityHits('fetch_all_by_usr_moments',
                                           usr_space=conformer.usr_space, usr_moments=conformer.usr_moments)