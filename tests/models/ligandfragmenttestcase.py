from credoscript import models
from tests import CredoEntityTestCase

class LigandFragmentTestCase(CredoEntityTestCase):
    def setUp(self):
        self.ligand_fragment = models.LigandFragment.query.limit(1).first()

    # direct one-to-one relationship
    def test_has_ligand(self):
        self.assertOneToOne(self.ligand_fragment, 'Ligand', models.Ligand)

    def test_has_ligand_component(self):
        self.assertOneToOne(self.ligand_fragment, 'LigandComponent', models.LigandComponent)

    def test_has_fragment(self):
        self.assertOneToOne(self.ligand_fragment, 'Fragment', models.Fragment)

    # direct one-to-many mappings
    def test_has_atoms(self):
        self.assertDynamicRelationship(self.ligand_fragment, 'Atoms', models.Atom)

    def test_has_contacts(self):
        self.assertDynamicRelationship(self.ligand_fragment, 'Contacts', models.Contact)
