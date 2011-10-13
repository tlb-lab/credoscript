import os
import sys
import json
import warnings

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SAWarning, ProgrammingError

# CONFIGURATION
CREDOSCRIPT_PATH= os.path.dirname(os.path.realpath(__file__))
CONFIG_PATH     = os.path.join(CREDOSCRIPT_PATH, 'config.json')

# EXIT IF THE CONFIGURATION FILE DOES NOT EXIST
if not os.path.exists(CONFIG_PATH):
    raise IOError("""cannot find the configuration file config.json in credoscript
                  directory. Did you forget to rename config-default.json?""")

CONFIG          = json.loads(open(CONFIG_PATH).read())

# DATABASE CONNECTION
url             = '{driver}://{user}:{passwd}@{host}:{port}/{db}'.format(**CONFIG['connection'])
engine          = create_engine(url, echo=CONFIG['debug']['SQL'])
metadata        = MetaData(bind=engine)

# SUPPRESS WARNINGS CONCERNING POSTGRESQL-SPECIFIC TYPES AND INDEXES
warnings.simplefilter('ignore', SAWarning)

# REFLECT ALL THE REQUIRED SCHEMAS
metadata.reflect(schema='credo')
metadata.reflect(schema='pdbchem')
metadata.reflect(schema='pdb')

# DATABASE SESSION
Session     = sessionmaker(bind=engine, autocommit=True)
session     = Session()

# CHECK IF REQUIRED EXTENSIONS/FUNCTIONS IS INSTALLED ON THE SERVER
HAS_RDKIT_CARTRIDGE = engine.execute("SELECT true where exists (select proname FROM pg_proc where proname = 'rdkit_version')").scalar()

# DETERMINE IF RDKIT IS INSTALLED LOCALLY
try:
    import rdkit
    HAS_RDKIT = True
except ImportError:
    HAS_RDKIT = False

# REQUIRES HIGHER VERSION OF PSYCOPG2
# psycopg2.extras.register_composite('vector', globally=True)

# DO NOT MAP AGAINST CLASS
binding_sites = metadata.tables['credo.binding_sites']
binding_site_atom_surface_areas = metadata.tables['credo.binding_site_atom_surface_areas']
chem_comp_fragment_atoms = metadata.tables['pdbchem.chem_comp_fragment_atoms']
ligand_molstrings = metadata.tables['credo.ligand_molstrings']
ligand_fragments = metadata.tables['credo.ligand_fragments']
ligand_fragment_atoms = metadata.tables['credo.ligand_fragment_atoms']
ligand_usr = metadata.tables['credo.ligand_usr']
citations = metadata.tables['pdb.citations']
disordered_regions = metadata.tables['pdb.disordered_regions']