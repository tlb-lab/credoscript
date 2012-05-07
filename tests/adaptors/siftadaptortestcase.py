from credoscript import adaptors, models
from tests import CredoAdaptorTestCase

class SIFtAdaptorTestCase(CredoAdaptorTestCase):
    def setUp(self):
        self.adaptor = adaptors.SIFtAdaptor()

    def _check_sift(self, result):
        for row in result:
            residue, sift = row[0], row[1:]
            self.assertIsInstance(residue, models.Residue)
            self.assertEqual(len(sift), 13)

    def test_fetch_by_residue_id(self):
        """Fetch the SIFt of a single residue"""
        residue = models.Residue.query.filter_by(path='2P33/0/A/SER`72').first()
        result = self.adaptor.fetch_by_residue_id(residue.residue_id,
                                                  residue.biomolecule_id)

        # SIFt of a residue is only a single row
        self.assertEqual(len(result), 13)

    def test_fetch_by_ligand_id(self):
        """Fetch the SIFt of a ligand"""
        ligand = models.Ligand.query.filter_by(path='2P33/0/A/J07`507').first()
        result = self.adaptor.fetch_by_ligand_id(ligand.ligand_id,
                                                 ligand.biomolecule_id)

        self._check_sift(result)

    def test_fetch_by_ligand_fragment_id(self):
        """Fetch the SIFt of a ligand fragment"""
        ligand = models.Ligand.query.filter_by(path='2P33/0/A/J07`507').first()
        lf = ligand.LigandFragments[4]
        result = self.adaptor.fetch_by_ligand_id(lf.ligand_fragment_id,
                                                 ligand.biomolecule_id)

        self._check_sift(result)

    def test_fetch_by_ligand_id_and_atom_names(self):
        """Fetch the SIFt with a ligand_id and atom names"""
        ligand = models.Ligand.query.filter_by(path='3EFW/0/A/AK8`404').first()
        result = self.adaptor.fetch_by_ligand_id_and_atom_names(ligand.ligand_id,
                                                                ligand.biomolecule_id,
                                                                [['C7', 'C6', 'C5', 'C9', 'N3', 'C8', 'C2', 'C3', 'C4', 'N2', 'C1', 'N1']])

        self._check_sift(result)
    
    def test_fetch_by_own_chain_id(self):
        """Fetch the SIFt of a chain"""
        chain = models.Chain.query.filter_by(path='2P33/0/A').first()
        result = self.adaptor.fetch_by_own_chain_id(chain.chain_id,
                                                    chain.biomolecule_id)

        self._check_sift(result)