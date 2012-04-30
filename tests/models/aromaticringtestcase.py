from credoscript import models
from credoscript.support.vector import Vector

from tests import CredoEntityTestCase

class AromaticRingTestCase(CredoEntityTestCase):
    def setUp(self):
        self.entity = models.AromaticRing.query.get(1)

    def test_has_biomolecule(self):
        """test if AromaticRing has a Biomolecule parent"""
        self.assertOneToOne(self.entity, 'Biomolecule', models.Biomolecule)

    def test_has_residue(self):
        """test if AromaticRing has a Residue parent"""
        self.assertOneToOne(self.entity, 'Residue', models.Residue)

    def test_has_peptide(self):
        """test if AromaticRing has a Residue parent"""
        self.assertOneToOne(self.entity, 'Peptide', models.Peptide)

    def test_has_nucleotide(self):
        """test if AromaticRing has a Residue parent"""
        self.assertOneToOne(self.entity, 'Nucleotide', models.Nucleotide)

    def test_has_saccharide(self):
        """test if AromaticRing has a Residue parent"""
        self.assertOneToOne(self.entity, 'Saccharide', models.Saccharide)

    def test_centroid(self):
        """test if AromaticRing has a Centroid property of type Vector"""
        self.assertIsInstance(self.entity.Centroid, Vector)

    def test_normal(self):
        """test if AromaticRing has a Normal property of type Vector"""
        self.assertIsInstance(self.entity.Normal, Vector)

    def test_has_atoms(self):
        """test if AromaticRing has Atoms"""
        self.assertDynamicRelationship(self.entity, 'Atoms', models.Atom)

    def test_has_ring_interactions(self):
        """test if AromaticRing has a relationship to RingInteraction"""
        self.assertDynamicRelationship(self.entity, 'RingInteractions', models.RingInteraction)

    def test_has_atom_ring_interactions(self):
        """test if AromaticRing has a relationship to AtomRingInteraction"""
        self.assertDynamicRelationship(self.entity, 'AtomRingInteractions', models.AtomRingInteraction)