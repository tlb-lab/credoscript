from credoscript import models
from tests import CredoEntityTestCase

class BiomoleculeTestCase(CredoEntityTestCase):
    def setUp(self):
        self.entity = models.Biomolecule.query.limit(1).first()

    # test overloaded methods

    def test_getitem(self):
        """
        biomolecule.__getitem__(pdb_chain_id) should return the chain having
        the input PDB Chain ID.
        """
        a = self.entity.Chains.all()
        b = [self.entity[c.pdb_chain_id] for c in a]

        self.assertListEqual(a,b)

    def test_iter(self):
        a = self.entity.Chains.all()
        b = [chain for chain in self.entity]

        self.assertListEqual(a,b)

    # direct one-to-one relationship

    def test_has_structure(self):
        self.assertOneToOne(self.entity, 'Structure', models.Structure)

    # direct one-to-many mappings

    def test_has_chains(self):
        self.assertDynamicRelationship(self.entity, 'Chains', models.Chain)

    def test_has_chain_map(self):
        self.assertMappedCollection(self.entity, 'ChainMap')

    def test_has_interfaces(self):
        self.assertDynamicRelationship(self.entity, 'Interfaces', models.Interface)

    def test_has_grooves(self):
        self.assertDynamicRelationship(self.entity, 'Grooves', models.Groove)

    def test_has_ligands(self):
        self.assertDynamicRelationship(self.entity, 'Ligands', models.Ligand)

    def test_has_residues(self):
        self.assertDynamicRelationship(self.entity, 'Residues', models.Residue)

    def test_has_peptides(self):
        self.assertDynamicRelationship(self.entity, 'Peptides', models.Peptide)

    def test_has_aromatic_rings(self):
        self.assertDynamicRelationship(self.entity, 'AromaticRings', models.AromaticRing)

    def test_has_ring_interactions(self):
        self.assertDynamicRelationship(self.entity, 'RingInteractions', models.RingInteraction)

    def test_has_atom_ring_interactions(self):
        self.assertDynamicRelationship(self.entity, 'AtomRingInteractions', models.AtomRingInteraction)

    def test_has_atoms(self):
        self.assertDynamicRelationship(self.entity, 'Atoms', models.Atom)