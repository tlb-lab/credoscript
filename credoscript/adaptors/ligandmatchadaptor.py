from sqlalchemy.sql.expression import and_, func

from credoscript import Session

class LigandMatchAdaptor(object):
    """
    This class is used to fetch ligand pattern matches, i.e. a set of ligand atoms
    that match a given substructure or SMARTS pattern.
    """
    def _fetch_matches(self, method, pattern, *expr):
        """
        """
        query = Ligand.query.join('MolString')
        query = query.join(ChemCompRDMol, ChemCompRDMol.het_id==Ligand.ligand_name)

        query = query.with_entities(Ligand.ligand_id, Ligand.biomolecule_id,
                                    LigandMolString.ism,
                                    func.openeye.match_atom_names(LigandMolString.oeb, pattern).label('atom_names'))

        query = query.filter(and_(getattr(ChemCompRDMol, method)(pattern), *expr))

        return [LigandMatch(pattern, *row) for row in query.all()]

    def fetch_substruct_matches(self, pattern, *expr):
        """
        Returns all the ligand matches whose ligands contain the given
        substructure.
        """
        return self._fetch_matches('contains', pattern, *expr)

    def fetch_smarts_matches(self, pattern, *expr):
        """
        Returns all the ligand matches whose ligands match the given SMARTS
        pattern.
        """
        return self._fetch_matches('matches', pattern, *expr)

from ..models.ligand import Ligand
from ..models.ligandmolstring import LigandMolString
from ..models.chemcomprdmol import ChemCompRDMol
from ..models.ligandmatch import LigandMatch