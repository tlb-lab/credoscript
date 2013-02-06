from credoscript import models
from tests import CredoEntityTestCase

class BindingSiteTestCase(CredoEntityTestCase):
    def setUp(self):
        self.bs = models.BindingSite.query.limit(1).first()

    # direct one-to-one relationship

    def test_has_ligand(self):
        self.assertOneToOne(self.bs, 'Ligand', models.Ligand)

    # direct one-to-many mappings

    def test_has_domains(self):
        self.assertDynamicRelationship(self.bs, 'Domains', models.Domain)

if __name__ == '__main__':
    import unittest
    unittest.main()
