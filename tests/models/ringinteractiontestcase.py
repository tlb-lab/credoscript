from credoscript import models
from credoscript.support.vector import Vector

from tests import CredoEntityTestCase

class RingInteractionTestCase(CredoEntityTestCase):
    def setUp(self):
        self.entity = models.RingInteraction.query.limit(1).first()

    def test_has_biomolecule(self):
        """test if RingInteraction has a Biomolecule parent"""
        self.assertOneToOne(self.entity, 'Biomolecule', models.Biomolecule)

    def test_has_aromatic_ring_bgn(self):
        """test if RingInteraction has a AromaticRingBgn"""
        self.assertOneToOne(self.entity, 'AromaticRingBgn', models.AromaticRing)

    def test_has_aromatic_ring_end(self):
        """test if RingInteraction has a AromaticRingEnd"""
        self.assertOneToOne(self.entity, 'AromaticRingEnd', models.AromaticRing)

    def test_has_closest_atom_bgn(self):
        """test if RingInteraction has a ClosestAtomBgn"""
        self.assertOneToOne(self.entity, 'ClosestAtomBgn', models.Atom)

    def test_has_closest_atom_end(self):
        """test if RingInteraction has a ClosestAtomEnd"""
        self.assertOneToOne(self.entity, 'ClosestAtomEnd', models.Atom)