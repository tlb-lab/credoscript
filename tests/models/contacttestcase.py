from credoscript import models
from tests import CredoEntityTestCase

class ContactTestCase(CredoEntityTestCase):
    def setUp(self):
        self.entity = models.Contact.query.get(12345)
    
    def test_has_atom_bgn(self):
        """test if Contact has a relationship to Atom (AtomBgn)"""
        self.assertOneToOne(self.entity, 'AtomBgn', models.Atom)
    
    def test_has_atom_end(self):
        """test if Contact has a relationship to Atom (AtomEnd)"""
        self.assertOneToOne(self.entity, 'AtomEnd', models.Atom)
    
    def test_has_sift(self):
        """"""
        self.assertEqual(len(self.entity.sift), 13)