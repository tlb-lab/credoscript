from sqlalchemy.sql.expression import and_, func

from credoscript import Session

class LigandMatchAdaptor(object):
    """
    This class is used to fetch ligand pattern matches, i.e. a set of ligand atoms
    that match a given substructure or SMARTS pattern.
    """
    def fetch_substruct_matches(self, pattern, *expr):
        """
        """
        session = Session()

        query = session.query(Ligand.ligand_id, Ligand.biomolecule_id, LigandMolString.ism,
                              func.openeye.match_atom_names(LigandMolString.oeb, pattern).label('atom_names'))
        query = query.join(LigandMolString, LigandMolString.ligand_id==Ligand.ligand_id)
        query = query.join(ChemCompRDMol, ChemCompRDMol.het_id==Ligand.ligand_name)
        query = query.filter(and_(ChemCompRDMol.contains(pattern), *expr))

        return [LigandMatch(pattern, *row) for row in query.all()]

    def fetch_smarts_matches(self, pattern, *expr):
        """
        """
        session = Session()

        query = session.query(Ligand.ligand_id, Ligand.biomolecule_id, LigandMolString.ism,
                              func.openeye.match_atom_names(LigandMolString.oeb, pattern).label('atom_names'))
        query = query.join(LigandMolString, LigandMolString.ligand_id==Ligand.ligand_id)
        query = query.join(ChemCompRDMol, ChemCompRDMol.het_id==Ligand.ligand_name)
        query = query.filter(and_(ChemCompRDMol.matches(pattern), *expr))

        return [LigandMatch(pattern, *row) for row in query.all()]

from ..models.ligand import Ligand
from ..models.ligandmolstring import LigandMolString
from ..models.chemcomprdmol import ChemCompRDMol
from ..models.ligandmatch import LigandMatch