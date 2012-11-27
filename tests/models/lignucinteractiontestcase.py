from credoscript import models
from tests import CredoEntityTestCase

class LigNucInteractionTestCase(CredoEntityTestCase):
    def setUp(self):
        self.lignucint = models.LigNucInteraction.query.limit(1).first()

    # test overloaded methods

    def test_has_biomolecule(self):
        self.assertOneToOne(self.lignucint, 'Biomolecule', models.Biomolecule)

    def test_has_ligand(self):
        self.assertOneToOne(self.lignucint, 'Ligand', models.Ligand)

    def test_has_oligonucleotide(self):
        self.assertOneToOne(self.lignucint, 'Oligonucleotide', models.Chain)