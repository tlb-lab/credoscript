from credoscript import models
from tests import CredoEntityTestCase

class ProtFragmentTestCase(CredoEntityTestCase):
    def setUp(self):
        self.entity = models.ProtFragment.query.filter_by(path='101M/0/A/PF:9').first()

    def test_has_chain(self):
        """test if ProtFragment has a Chain parent"""
        self.assertOneToOne(self.entity, 'Chain', models.Chain)

    def test_has_prot_fragment_n(self):
        """test if ProtFragment has a N-terminal neighbour"""
        self.assertOneToOne(self.entity, 'ProtFragmentN', models.ProtFragment)

    def test_has_prot_fragment_c(self):
        """test if ProtFragment has a C-terminal neighbour"""
        self.assertOneToOne(self.entity, 'ProtFragmentC', models.ProtFragment)

    def test_has_peptides(self):
        """test if ProtFragment has a relationship to Peptide"""
        self.assertDynamicRelationship(self.entity, 'Peptides', models.Peptide)