from collections import Iterable

from credoscript import models
from tests import CredoEntityTestCase

class StructureTestCase(CredoEntityTestCase):
    def setUp(self):
        self.structure = models.Structure.query.filter_by(pdb='2P33').first()
    
    # test overloaded methods
    
    def test_getitem(self):
        """
        structure.__getitem__(assembly_serial) should return the biomolecule having
        the input assembly serial number.
        """
        a = self.structure.Biomolecules.all()
        b = [self.structure[b.assembly_serial] for b in self.structure.Biomolecules.all()]
        
        self.assertListEqual(a,b)
    
    def test_iter(self):
        a = self.structure.Biomolecules.all()
        b = [biomolecule for biomolecule in self.structure]
        
        self.assertListEqual(a,b)
    
    # direct one-to-many mappings
    
    def test_has_biomolecules(self):
        self.assertDynamicRelationship(self.structure, 'Biomolecules', models.Biomolecule)
    
    def test_has_biomolecule_map(self):
        self.assertMappedCollection(self.structure, 'BiomoleculeMap')
    
    def test_has_xrefs(self):
        self.assertDynamicRelationship(self.structure, 'XRefs', models.XRef)
    
    # other methods
    
    def test_abstracts(self):
        self.assertIsInstance(self.structure.abstracts, Iterable)
        