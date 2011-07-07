"""
Each contact in CREDO is classified based on the kind of macromolecular interaction
it takes part in. This file serves as a namespace containing the mapping between
the interaction_type_id used in the contacts table and the corresponding description.
"""

PRO_PRO = 1
PRO_DNA = 2
PRO_RNA = 3
PRO_SAC = 4
PRO_LIG = 5
PRO_WAT = 6
DNA_DNA = 7
DNA_RNA = 8
DNA_SAC = 9
DNA_LIG = 10
DNA_WAT = 11
RNA_RNA = 12
RNA_SAC = 13
RNA_LIG = 14
RNA_WAT = 15
SAC_SAC = 16
SAC_LIG = 17
SAC_WAT = 18
LIG_LIG = 19
LIG_WAT = 20
UNKNOWN = 21