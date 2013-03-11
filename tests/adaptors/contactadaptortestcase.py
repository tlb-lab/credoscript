from credoscript import adaptors, models
from tests import CredoAdaptorTestCase

class ContactAdaptorTestCase(CredoAdaptorTestCase):
    def setUp(self):
        self.adaptor = adaptors.ContactAdaptor()
        self.expected_entity = models.Contact

    def test_fetch_by_contact_id(self):
        """Fetch a single Contact by contact_id"""
        self.assertSingleResult('fetch_by_contact_id', 1, 1)

    def test_fetch_all_by_atom_id(self):
        """Fetch all contacts an atom has by atom_id"""
        self.assertPaginatedResult('fetch_all_by_atom_id', 1, 1)

    def test_fetch_all_by_residue_id(self):
        """Fetch all contacts a residue has by residue_id"""
        self.assertPaginatedResult('fetch_all_by_residue_id', 1, 1)

    def test_fetch_all_by_ligand_id(self):
        """Fetch all contacts a ligand has by ligand_id"""
        ligand = models.Ligand.query.filter_by(ligand_name='J07').first()
        self.assertPaginatedResult('fetch_all_by_ligand_id',
                                   ligand.ligand_id, ligand.biomolecule_id)

    def test_fetch_all_by_chain_id(self):
        """Fetch all contacts a chain has by chain_id"""
        chain = models.Chain.query.limit(1).first()
        self.assertPaginatedResult('fetch_all_by_chain_id',
                                   chain.chain_id, chain.biomolecule_id)

    def test_fetch_all_by_interface_id(self):
        """Fetch all contacts a chain has by interface_id"""
        interface = models.Interface.query.limit(1).first()
        self.assertPaginatedResult('fetch_all_by_interface_id',
                                   interface.interface_id, interface.biomolecule_id)

    def test_fetch_all_by_groove_id(self):
        """Fetch all contacts a groove has by groove_id"""
        groove = models.Groove.query.get(1)
        self.assertPaginatedResult('fetch_all_by_groove_id',
                                   groove.groove_id, groove.biomolecule_id)

    def test_fetch_all_by_ligand_fragment_id(self):
        """Fetch all contacts a ligand fragment has by ligand_fragment_id"""
        ligand = models.Ligand.query.filter_by(path='2ZJV/1/A/CT4`301').first()
        lf = ligand.LigandFragments[3]
        self.assertPaginatedResult('fetch_all_by_ligand_fragment_id',
                                   lf.ligand_fragment_id, ligand.ligand_id)

    def test_fetch_by_ligand_id_and_atom_names(self):
        """Fetch the SIFt with a ligand_id and atom names"""
        ligand = models.Ligand.query.filter_by(path='3EFW/1/A/AK8`404').first()
        result = self.adaptor.fetch_all_by_ligand_id_and_atom_names(ligand.ligand_id,
                                                                    ligand.biomolecule_id,
                                                                    [['C7', 'C6', 'C5', 'C9', 'N3', 'C8', 'C2', 'C3', 'C4', 'N2', 'C1', 'N1']])
