from credoscript import models
from tests import CredoEntityTestCase

class LigandTestCase(CredoEntityTestCase):
    def setUp(self):
        self.ligand = models.Ligand.query.filter_by(path='2P33/0/A/J07`507').first()

    # test overloaded methods
    def test_len(self):
        self.assertEqual(len(self.ligand), self.ligand.num_hvy_atoms,
                         "method __len__ of Ligand differs from num_hvy_atoms.")

    # direct one-to-one relationship

    def test_has_biomolecule(self):
        self.assertOneToOne(self.ligand, 'Biomolecule', models.Biomolecule)

    def test_has_molstring(self):
        self.assertOneToOne(self.ligand, 'MolString', models.LigandMolString)

    # direct one-to-many mappings

    def test_has_atoms(self):
        self.assertDynamicRelationship(self.ligand, 'Atoms', models.Atom)

    def test_has_aromatic_rings(self):
        self.assertDynamicRelationship(self.ligand, 'AromaticRings', models.AromaticRing)

    def test_has_components(self):
        self.assertDynamicRelationship(self.ligand, 'Components', models.LigandComponent)

    def test_has_residues(self):
        self.assertDynamicRelationship(self.ligand, 'Residues', models.Residue)

    def test_has_ligand_fragments(self):
        self.assertDynamicRelationship(self.ligand, 'LigandFragments', models.LigandFragment)

    def test_has_xrefs(self):
        self.assertDynamicRelationship(self.ligand, 'XRefs', models.XRef)

    def test_has_atom_ring_interactions(self):
        self.assertDynamicRelationship(self.ligand, 'AtomRingInteractions', models.AtomRingInteraction)

    def test_has_proximal_residues(self):
        self.assertDynamicRelationship(self.ligand, 'ProximalResidues', models.Residue)

    def test_has_proximal_atoms(self):
        self.assertDynamicRelationship(self.ligand, 'ProximalAtoms', models.Atom)

    def test_has_proximal_water(self):
        self.assertDynamicRelationship(self.ligand, 'ProximalWater', models.Atom)

    def test_has_proximal_prot_fragments(self):
        self.assertDynamicRelationship(self.ligand, 'ProximalProtFragments', models.ProtFragment)

    def test_has_contacts(self):
        self.assertDynamicRelationship(self.ligand, 'Contacts', models.Contact)

    def test_has_ring_interactions(self):
        self.assertDynamicRelationship(self.ligand, 'RingInteractions', models.RingInteraction)

    def test_has_binding_site_residues(self):
        self.assertDynamicRelationship(self.ligand, 'BindingSiteResidues', models.BindingSiteResidue)

if __name__ == '__main__':
    import unittest
    unittest.main()