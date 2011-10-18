from credoscript import *

# FETCH PDB ENTRY 3CS9
s = StructureAdaptor().fetch_by_pdb('3cs9')
print s.title


# 3CS9 CONTAINS 4 BIOLOGICAL ASSEMBLIES
print s.Biomolecules

# TAKE THE FIRST
b = s[1]

# LIGANDS OF THE FIRST BIOMOLECULE: NILOTINIB
print b.Ligands

l = b.Ligands[0]

# GET SOLVENT-ACCESSIBLE SURFACE AREA OF THE LIGAND IN THE APO STATE
print l.get_buried_surface_area(projection='ligand', state='apo')

# BOUND STATE
print l.get_buried_surface_area(projection='ligand', state='bound')


# DELTA: HOW MUCH ASA OF THE LIGAND BECOMES INACCESSIBLE UPON BINDING?
print l.get_buried_surface_area(projection='ligand', state='delta')

# HOW MUCH OF THAT IS POLAR SURFACE AREA?
print l.get_buried_surface_area(Atom.is_polar==True, projection='ligand', state='delta')

# SAME AS ABOVE BUT BROKEN DOWN INTO INDIVIDUAL LIGAND ATOMS
print l.get_buried_surface_area(Atom.is_polar==True, projection='ligand', state='apo', atom_areas=True)