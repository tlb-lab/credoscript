from credoscript import adaptors, models
from tests import CredoAdaptorTestCase

class AtomAdaptorTestCase(CredoAdaptorTestCase):
    def setUp(self):
        self.adaptor = adaptors.AtomAdaptor()
        self.expected_entity = models.Atom

    def test_fetch_by_atom_id(self):
        """Fetch a single Atom by atom_id"""
        atom = models.Atom.query.limit(1).first()
        self.assertSingleResult('fetch_by_atom_id',
                                atom.atom_id, atom.biomolecule_id)

    def test_fetch_all_by_ligand_id(self):
        """Fetch all atoms that comprise a ligand by ligand_id"""
        ligand = models.Ligand.query.filter(models.Ligand.ligand_name=='STI').first()
        self.assertPaginatedResult('fetch_all_by_ligand_id',
                                   ligand.ligand_id, ligand.biomolecule_id)

    def test_fetch_all_by_chain_id(self):
        """Fetch all atoms that comprise a chain by chain_id"""
        chain = models.Chain.query.filter(models.Chain.pmatches('2P33/0/A')).first()
        self.assertPaginatedResult('fetch_all_by_chain_id',
                                   chain.chain_id, chain.biomolecule_id)

    def test_fetch_all_in_contact_with_ligand_id(self):
        """Fetch all atoms that are interacting with the ligand_id."""
        ligand = models.Ligand.query.filter(models.Ligand.ligand_name=='STI').first()
        self.assertPaginatedResult('fetch_all_in_contact_with_ligand_id',
                                   ligand.ligand_id, ligand.biomolecule_id)

    def test_fetch_all_water_in_contact_with_atom_id(self):
        """Fetch all (water) atoms that are interacting with the atom_id."""
        atom = models.Atom.query.limit(1).first()
        self.assertPaginatedResult('fetch_all_water_in_contact_with_atom_id',
                                   atom.atom_id, atom.biomolecule_id)

    def test_fetch_all_water_in_contact_with_residue_id(self):
        """Fetch all (water) atoms that are interacting with the residue_id."""
        atom = models.Atom.query.limit(1).first()
        self.assertPaginatedResult('fetch_all_water_in_contact_with_residue_id',
                                   atom.residue_id, atom.biomolecule_id)

    def test_fetch_all_water_in_contact_with_ligand_id(self):
        """Fetch all (water) atoms that are interacting with the ligand_id."""
        ligand = models.Ligand.query.filter(models.Ligand.ligand_name=='STI').first()
        self.assertPaginatedResult('fetch_all_water_in_contact_with_ligand_id',
                                   ligand.ligand_id, ligand.biomolecule_id)

    def test_fetch_all_in_contact_with_ligand_fragment_id(self):
        """Fetch all atoms that are interacting with the ligand_fragment_id."""
        ligand = models.Ligand.query.filter(models.Ligand.ligand_name=='STI').first()
        lf = ligand.LigandFragments.first()

        self.assertPaginatedResult('fetch_all_in_contact_with_ligand_fragment_id',
                                   lf.ligand_fragment_id, ligand.biomolecule_id)

    def test_fetch_all_water_in_contact_with_interface_id(self):
        """Fetch all atoms that are interacting with the ligand_fragment_id."""
        interface = models.Interface.query.filter(models.Interface.pmatches('11GS/1/I:A-B')).first()

        self.assertPaginatedResult('fetch_all_water_in_contact_with_interface_id',
                                   interface.interface_id, interface.biomolecule_id)

    def test_fetch_all_by_ligand_id_and_atom_names(self):
        """Fetch all atoms by ligand identifier and list of atom names"""
        match = adaptors.LigandMatchAdaptor().fetch_substruct_matches('c1cc(cnc1)c2ccncn2')[0]
        self.assertPaginatedResult('fetch_all_by_ligand_id_and_atom_names',
                                   match.ligand_id, match.biomolecule_id, match.atom_names)
