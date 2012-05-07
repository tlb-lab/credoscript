from credoscript import adaptors, models
from tests import CredoEntityTestCase

class LigandMatchTestCase(CredoEntityTestCase):
    def setUp(self):
        self.entity = adaptors.LigandMatchAdaptor().fetch_substruct_matches('c1cc(cnc1)c2ccncn2')[0]

    def test_has_ligand(self):
        """Test if the match has a ligand property"""
        self.assertOneToOne(self.entity, 'Ligand', models.Ligand)

    def test_has_atoms(self):
        """test if the atoms of the match can be retrieved"""
        self.assertDynamicRelationship(self.entity, 'Hetatms', models.Atom)

    def test_has_contacts(self):
        """Test if the contacts of the match can be retrieved"""
        self.assertDynamicRelationship(self.entity, 'Contacts', models.Contact)

    def test_has_proximal_residues(self):
        """Test if the proximal residues of the match can be retrieved"""
        self.assertDynamicRelationship(self.entity, 'ProximalResidues', models.Residue)

    def test_has_sift(self):
        """Test the SIFt of the match"""
        for row in self.entity.sift():
            residue, sift = row[0], row[1:]
            self.assertIsInstance(residue, models.Residue)
            self.assertEqual(len(sift), 13)