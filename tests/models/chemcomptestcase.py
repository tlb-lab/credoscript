from credoscript import models
from tests import CredoEntityTestCase

class ChemCompTestCase(CredoEntityTestCase):
    def setUp(self):
        self.chemcomp = models.ChemComp.query.filter_by(het_id='STI').first()

    # test overloaded methods

    def test_len(self):
        self.assertEqual(len(self.chemcomp), self.chemcomp.num_hvy_atoms,
                         "method __len__ of ChemComp differs from num_hvy_atoms.")

    def test_or(self):
        "test the overloaded USR similarity operator"
        self.assertAlmostEqual(self.chemcomp | self.chemcomp, 1.0)

    def test_mod(self):
        "test the overloaded 2D similarity operator"
        self.assertAlmostEqual(self.chemcomp % self.chemcomp, 1.0)

    # direct one-to-one relationship

    def test_has_molstring(self):
        self.assertOneToOne(self.chemcomp, 'MolString', models.ChemCompMolString)

    def test_has_rdmol(self):
        self.assertOneToOne(self.chemcomp, 'RDMol', models.ChemCompRDMol)

    def test_has_rdfp(self):
        self.assertOneToOne(self.chemcomp, 'RDFP', models.ChemCompRDFP)

    # direct one-to-many mappings

    def test_has_chem_comp_fragments(self):
        self.assertDynamicRelationship(self.chemcomp, 'ChemCompFragments', models.ChemCompFragment)

    def test_has_conformers(self):
        self.assertDynamicRelationship(self.chemcomp, 'Conformers', models.ChemCompConformer)

    def test_has_fragments(self):
        self.assertDynamicRelationship(self.chemcomp, 'Fragments', models.Fragment)

    def test_has_ligands(self):
        self.assertDynamicRelationship(self.chemcomp, 'Ligands', models.Ligand)

    def test_has_xrefs(self):
        self.assertDynamicRelationship(self.chemcomp, 'XRefs', models.XRef)

    def test_has_xref_map(self):
        self.assertMappedCollection(self.chemcomp, 'XRefMap')
