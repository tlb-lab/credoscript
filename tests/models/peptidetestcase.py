from credoscript import models
from tests import CredoEntityTestCase

class PeptideTestCase(CredoEntityTestCase):
    def setUp(self):
        self.entity = models.Peptide.query.limit(1).first()

    def test_getitem(self):
        """
        residue.__getitem__(atom_name, alt_loc) should return the atom matching
        the identifiers.
        """
        atoms = self.entity.Atoms.all()
        b = [self.entity[atom.atom_name, atom.alt_loc] for atom in atoms]

        self.assertListEqual(atoms,b)

    def test_iter(self):
        atoms = self.entity.Atoms.all()
        self.assertListEqual(atoms, [atom for atom in self.entity])

    def test_has_atoms(self):
        self.assertDynamicRelationship(self.entity, 'Atoms', models.Atom)

    def test_has_atom_map(self):
        self.assertMappedCollection(self.entity, 'AtomMap')

    def test_has_aromatic_rings(self):
        self.assertDynamicRelationship(self.entity, 'AromaticRings', models.AromaticRing)

    def test_has_contacts(self):
        self.assertDynamicRelationship(self.entity, 'Contacts', models.Contact)

    def test_has_proximal_water(self):
        self.assertDynamicRelationship(self.entity, 'ProximalWater', models.Atom)
    
    def test_has_peptide_features(self):
        self.assertDynamicRelationship(self.entity, 'Features', models.PeptideFeature)
    
    def test_has_feature_map(self):
        self.assertMappedCollection(self.entity, 'FeatureMap')