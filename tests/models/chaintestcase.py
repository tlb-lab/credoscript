from credoscript import models
from tests import CredoEntityTestCase

class ChainTestCase(CredoEntityTestCase):
    def setUp(self):
        self.entity = models.Chain.query.limit(1).first()

    def test_getitem(self):
        """
        biomolecule.__getitem__(pdb_chain_id) should return the chain having
        the input PDB Chain ID.
        """
        residues = self.entity.Residues.all()
        test = [self.entity[r.res_num, r.ins_code] for r in residues]

        self.assertListEqual(residues, test)

    def test_iter(self):
        """Test the for residue in chain syntax"""
        a = self.entity.Residues.all()
        b = [res for res in self.entity]

        self.assertListEqual(a,b)

    def test_has_biomolecule(self):
        self.assertOneToOne(self.entity, 'Biomolecule', models.Biomolecule)

    def test_has_residues(self):
        """test the chain.Residues dynamic relationship"""
        self.assertDynamicRelationship(self.entity, 'Residues', models.Residue)

    def test_has_residue_map(self):
        self.assertMappedCollection(self.entity, 'ResidueMap')

    def test_has_peptides(self):
        """test the chain.Peptides dynamic relationship"""
        self.assertDynamicRelationship(self.entity, 'Peptides', models.Peptide)

    def test_has_nucleotides(self):
        """test the chain.Peptides dynamic relationship"""
        self.assertDynamicRelationship(self.entity, 'Nucleotides', models.Nucleotide)

    def test_has_prot_fragments(self):
        """test the chain.Peptides dynamic relationship"""
        self.assertDynamicRelationship(self.entity, 'ProtFragments', models.ProtFragment)

    def test_has_xrefs(self):
        self.assertDynamicRelationship(self.entity, 'XRefs', models.XRef)

    def test_has_variations(self):
        """test the chain.Variations dynamic relationship"""
        self.assertDynamicRelationship(self.entity, 'Variations', models.Variation)

    def test_has_contacts(self):
        """test the chain.Variations dynamic relationship"""
        self.assertDynamicRelationship(self.entity, 'Contacts', models.Contact)

    def test_has_proximal_ligands(self):
        """test the chain.ProximalLigands dynamic relationship"""
        self.assertDynamicRelationship(self.entity, 'ProximalLigands', models.Ligand)

    def test_disordered_regions(self):
        """test the disordered_regions method of Chain"""
        chain = models.Chain.query.filter_by(path='2P33/0/A').first()
        disordered_regions = chain.disordered_regions()

        assert isinstance(disordered_regions, list), "disordered_regions() does not return a list."

    def test_residue_sift(self):
        """"""
        self.assertValidSIFt(self.entity, 'residue_sift')