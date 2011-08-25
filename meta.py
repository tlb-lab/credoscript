import os
import json
import warnings

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SAWarning, ProgrammingError

# CONFIGURATION
CREDOSCRIPT_PATH= os.path.dirname(os.path.realpath(__file__))
CONFIG_PATH     = os.path.join(CREDOSCRIPT_PATH, 'config.json')
CONFIG          = json.loads(open(CONFIG_PATH).read())

# DATABASE CONNECTION
url             = '{driver}://{user}:{passwd}@{host}:{port}/{db}'.format(**CONFIG['connection'])
engine          = create_engine(url, echo=CONFIG['debug']['SQL'])
credo           = MetaData(bind=engine)

# SUPPRESS WARNINGS CONCERNING POSTGRESQL-SPECIFIC TYPES AND INDEXES
warnings.simplefilter('ignore', SAWarning)

# REFLECT ALL THE REQUIRED SCHEMAS
credo.reflect(schema='credo')
credo.reflect(schema='pdbchem')
credo.reflect(schema='pdb')

# DATABASE SESSION
Session     = sessionmaker(bind=engine, autocommit=True)
session     = Session()

# CHECK IF REQUIRED EXTENSIONS/FUNCTIONS IS INSTALLED ON THE SERVER
HAS_RDKIT_CARTRIDGE = engine.execute("SELECT true where exists (select proname FROM pg_proc where proname = 'rdkit_version')").scalar()

# DETERMINE IF RDKIT IS INSTALLED
try:
    import rdkit
    HAS_RDKIT = True
except ImportError:
    HAS_RDKIT = False

# REQUIRES HIGHER VERSION OF PSYCOPG2
# psycopg2.extras.register_composite('vector', globally=True)

# DO NOT MAP AGAINST CLASS
binding_sites = credo.tables['credo.binding_sites']
binding_site_atom_surface_areas = credo.tables['credo.binding_site_atom_surface_areas']
chem_comp_fragment_atoms = credo.tables['pdbchem.chem_comp_fragment_atoms']
ligand_molstrings = credo.tables['credo.ligand_molstrings']
ligand_fragments = credo.tables['credo.ligand_fragments']
ligand_fragment_atoms = credo.tables['credo.ligand_fragment_atoms']
ligand_usr = credo.tables['credo.ligand_usr']
citations = credo.tables['pdb.citations']
disordered_regions = credo.tables['pdb.disordered_regions']