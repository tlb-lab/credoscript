from sqlalchemy.ext.hybrid import hybrid_method

from .model import Model

class ChemCompRDFP(Model):
    '''
    '''
    def __repr__(self):
        '''
        '''
        return '<ChemCompRDFP({self.het_id})>'.format(self=self)

    #@reconstructor
    #def init_on_load(self):
        #'''
        #Turns the rdmol column that is returned as a SMILES string back into an
        #RDMol object.
        #'''
        #self.torsion_fp = MolFromSmiles(self.torsion_fp)