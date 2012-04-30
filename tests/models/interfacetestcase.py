from credoscript import models
from tests import CredoEntityTestCase

class InterfaceTestCase(CredoEntityTestCase):
    def setUp(self):
        self.entity = models.Interface.query.get(12345)
     
    def test_has_biomolecule(self):
        """test if Interface has a relationship to Biomolecule"""
        self.assertOneToOne(self.entity, 'Biomolecule', models.Biomolecule)
    
    def test_has_chain_bgn(self):
        """test if Interface has a relationship to Chain (ChainBgn)"""
        self.assertOneToOne(self.entity, 'ChainBgn', models.Chain)
    
    def test_has_chain_end(self):
        """test if Interface has a relationship to Chain (ChainEnd)"""
        self.assertOneToOne(self.entity, 'ChainEnd', models.Chain)
    
    def test_has_residues(self):
        """retrieve all residues found in an interface"""
        self.assertDynamicRelationship(self.entity, 'Residues', models.Residue)
    
    def test_has_contacts(self):
        """test if Interface has a dynamic relationship to Contact"""
        self.assertDynamicRelationship(self.entity, 'Contacts', models.Contact)
    
    def test_has_proximal_water(self):
        """test if Interface has a dynamic relationship to Contact"""
        self.assertDynamicRelationship(self.entity, 'ProximalWater', models.Atom)