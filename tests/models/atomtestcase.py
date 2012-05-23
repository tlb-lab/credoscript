from credoscript import models
from credoscript.support.vector import Vector

from tests import CredoEntityTestCase

class AtomTestCase(CredoEntityTestCase):
    def setUp(self):
        self.entity = models.Atom.query.limit(1).first()

    def test__atom_name_alt_loc_tuple(self):
        """"""
        self.assertEqual(self.entity._atom_name_alt_loc_tuple,
                         (self.entity.atom_name, self.entity.alt_loc))

    def test_has_biomolecule(self):
        """test if Atom has a relationship to Biomolecule"""
        self.assertOneToOne(self.entity, 'Biomolecule', models.Biomolecule)

    def test_has_residue(self):
        """test if Atom has a relationship to Residue"""
        self.assertOneToOne(self.entity, 'Residue', models.Residue)

    def test_has_peptide(self):
        """test if Atom has a relationship to Peptide"""
        self.assertOneToOne(self.entity, 'Peptide', models.Peptide)

    def test_has_nucleotide(self):
        """test if Atom has a relationship to Nucleotide"""
        self.assertOneToOne(self.entity, 'Nucleotide', models.Nucleotide)

    def test_has_saccharide(self):
        """test if Atom has a relationship to Saccharide"""
        self.assertOneToOne(self.entity, 'Saccharide', models.Saccharide)

    def test_has_contacts(self):
        """test if Atom has a dynamic relationship to Contact"""
        self.assertDynamicRelationship(self.entity, 'Contacts', models.Contact)

    def test_has_contacts_bgn(self):
        """test if Atom has a relationship to Contact (ContactsBgn)"""
        self.assertDynamicRelationship(self.entity, 'ContactsBgn', models.Contact)

    def test_has_contacts_end(self):
        """test if Atom has a relationship to Contact (ContactsEnd)"""
        self.assertDynamicRelationship(self.entity, 'ContactsEnd', models.Contact)

    def test_has_proximal_water(self):
        """test if Atom has a relationship to Contact (ContactsEnd)"""
        self.assertDynamicRelationship(self.entity, 'ProximalWater', models.Atom)

    def test_vector(self):
        """test if Atom has a Vector property of the correct class"""
        self.assertIsInstance(self.entity.Vector, Vector)

    def test_is_polar(self):
        """test Atom.is_polar attribute"""
        if self.entity.element in ['N','O']:
            self.assertTrue(self.entity.is_polar)
        else:
            self.assertIn(self.entity.is_polar, [True, False])

    def test_is_mc(self):
        """test Atom.is_polar attribute"""
        if self.entity.atom_name in ['C','CA','N','O']:
            self.assertTrue(self.entity.is_mc)

        else:
            self.assertIn(self.entity.is_mc, [True, False])
