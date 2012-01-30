class LigandComponentAdaptor(object):
    '''
    '''
    def __init__(self):
        self.query = LigandComponent.query
       
    def fetch_by_ligand_component_id(self, ligand_component_id):
        '''
        '''
        return self.query.get(ligand_component_id)

    def fetch_by_residue_id(self, residue_id):
        '''
        '''
        return self.query.filter(LigandComponent.residue_id==residue_id).first()
    
    def fetch_all_by_het_id(self, het_id):
        '''
        '''
        query = self.query.join(
            (Residue, Residue.residue_id==LigandComponent.residue_id),
            (ChemComp, ChemComp.het_id==Residue.res_name))
        
        query = query.filter(ChemComp.het_id==het_id)
        
        return query.all()
        
from ..models.ligandcomponent import LigandComponent
from ..models.residue import Residue
from ..models.chemcomp import ChemComp