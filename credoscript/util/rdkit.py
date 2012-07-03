"""
This module contains convenience functions around RDKit to perform various
cheminformatics task related to credoscript.
"""
from __future__ import absolute_import

try:
    from rdkit.Chem import MolFromSmiles, RDKFingerprint
    from rdkit.DataStructs import TanimotoSimilarity
except ImportError:
    pass

from credoscript.util import requires

@requires.rdkit
def tanimoto_sml(queryism, targetism):
    """
    Returns the Tanimoto similarity between the two molecules in SMILES format.
    """
    # no Unicode here
    querymol = MolFromSmiles(str(queryism))
    targetmol = MolFromSmiles(str(targetism))

    if querymol and targetmol:
        queryfp = RDKFingerprint(querymol)
        targetfp = RDKFingerprint(targetmol)

        return TanimotoSimilarity(queryfp, targetfp)