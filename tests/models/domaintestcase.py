from credoscript import models
from credoscript.support.vector import Vector

from tests import CredoEntityTestCase

class DomainTestCase(CredoEntityTestCase):
    def setUp(self):
        self.entity = models.Domain.query.limit(1).first()

    def test_has_domain_peptides(self):
        """test if Domain has a dynamic relationship to DomainPeptide"""
        self.assertDynamicRelationship(self.entity, 'DomainPeptides', models.DomainPeptide)

    def test_has_peptides(self):
        """test if Domain has a dynamic relationship to Peptide"""
        self.assertDynamicRelationship(self.entity, 'Peptides', models.Peptide)

    def test_has_ligands(self):
        """test if Domain has a dynamic relationship to Ligand"""
        self.assertDynamicRelationship(self.entity, 'Ligands', models.Ligand)

    def test_has_chains(self):
        """test if Domain has a dynamic relationship to Peptide"""
        self.assertDynamicRelationship(self.entity, 'Chains', models.Chain)

class DomainPeptideCase(CredoEntityTestCase):
    def setUp(self):
        self.entity = models.DomainPeptide.query.limit(1).first()

    def test_has_peptide(self):
        """test if Atom has a relationship to Biomolecule"""
        self.assertOneToOne(self.entity, 'Peptide', models.Peptide)

    def test_has_domain(self):
        """test if Atom has a relationship to Biomolecule"""
        self.assertOneToOne(self.entity, 'Domain', models.Domain)