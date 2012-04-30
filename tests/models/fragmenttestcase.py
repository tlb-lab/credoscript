from credoscript import models
from tests import CredoEntityTestCase

class FragmentTestCase(CredoEntityTestCase):
    def setUp(self):
        self.entity = models.ChemComp.query.filter_by(het_id='STI').first().Fragments[-1]
    
    def test_has_chem_comp_fragments(self):
        """test if Fragment has a relationship to ChemCompFragment"""
        self.assertDynamicRelationship(self.entity, 'ChemCompFragments',
                                       models.ChemCompFragment)
    
    def test_has_chem_comps(self):
        """test if Fragment has a relationship to ChemComp"""
        self.assertDynamicRelationship(self.entity, 'ChemComps', models.ChemComp)
    
    def test_has_children(self):
        """test if Fragment has a working Children attribute"""
        self.assertDynamicRelationship(self.entity, 'Children', models.Fragment)
    
    def test_has_parents(self):
        """test if Fragment has a working Parents attribute"""
        self.assertDynamicRelationship(self.entity, 'Parents', models.Fragment)
    
    def test_has_leaves(self):
        """test if Fragment has a working Leaves attribute"""
        self.assertDynamicRelationship(self.entity, 'Leaves', models.Fragment)
    
    def test_has_descendants(self):
        """test if Fragment has a working Descendants attribute"""
        self.assertDynamicRelationship(self.entity, 'Descendants', models.Fragment)