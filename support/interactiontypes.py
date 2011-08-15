"""
Each contact in CREDO is classified based on the kind of macromolecular interaction
it takes part in. This file serves as a namespace containing the structural_interaction_type
used in the contacts table.
"""

UNKNOWN = 0
LIG_WAT = 3     # 2 + 1
LIG_LIG = 4
SAC_WAT = 5
SAC_LIG = 6
SAC_SAC = 8
RNA_WAT = 9
RNA_LIG = 10
RNA_SAC = 12
RNA_RNA = 16
DNA_WAT = 17
DNA_LIG = 18
DNA_SAC = 20    # 16 + 4
DNA_RNA = 24
DNA_DNA = 32
PRO_WAT = 33
PRO_LIG = 34
PRO_SAC = 36
PRO_RNA = 44
PRO_DNA = 48    # 32 + 16
PRO_PRO = 64    # 32 + 32



















