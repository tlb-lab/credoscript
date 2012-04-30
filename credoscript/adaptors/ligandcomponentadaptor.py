from credoscript.mixins.base import paginate

class LigandComponentAdaptor(object):
    """
    """
    def __init__(self, paginate=False, per_page=100):
        self.query = LigandComponent.query
        self.paginate = paginate
        self.per_page = per_page

    def fetch_by_ligand_component_id(self, ligand_component_id):
        """
        """
        return self.query.get(ligand_component_id)

    def fetch_by_residue_id(self, residue_id):
        """
        """
        return self.query.filter(LigandComponent.residue_id==residue_id).first()

    @paginate
    def fetch_all_by_het_id(self, het_id, **kwargs):
        """
        """
        query = self.query.join((ChemComp, ChemComp.het_id==LigandComponent.het_id))

        query = query.filter(ChemComp.het_id==het_id)

        return query

from ..models.ligandcomponent import LigandComponent
from ..models.residue import Residue
from ..models.chemcomp import ChemComp