from credoscript import models
from tests import CredoEntityTestCase

class ContactTestCase(CredoEntityTestCase):
    def setUp(self):
        ligand = models.Ligand.query.filter_by(path='2P33/0/A/J07`507').first()
        self.entity = ligand.Contacts.first()

    def test_has_atom_bgn(self):
        """test if Contact has a relationship to Atom (AtomBgn)"""
        self.assertOneToOne(self.entity, 'AtomBgn', models.Atom)

    def test_has_atom_end(self):
        """test if Contact has a relationship to Atom (AtomEnd)"""
        self.assertOneToOne(self.entity, 'AtomEnd', models.Atom)

    def test_has_sift(self):
        """"""
        self.assertEqual(len(self.entity.sift), 13)