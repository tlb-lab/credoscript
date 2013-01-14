import os
import json
import warnings

from sqlalchemy import create_engine, MetaData
from sqlalchemy.exc import SAWarning
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base

# register new data types
import credoscript.util.psycopg2

# credoscript version number scheme: year, month, release
# based on the database release
__version_info__ = (2013, 1, 1)
__version__ = '.'.join(map(str, __version_info__))

# the following modules will be imported with from credoscript import *
__all__ = ['adaptors', 'contrib', 'ext', 'models']

# configuration
CONFIG_PATH = os.path.join(__path__[0], 'config.json')

# exit if the configuration file does not exist
if not os.path.exists(CONFIG_PATH):
    raise IOError("cannot find the configuration file config.json in credoscript "
                  "directory. Did you rename config-default.json to config.json?")

config   = json.loads(open(CONFIG_PATH).read())

url      = URL(**config['connection'])
engine   = create_engine(url, echo=config['debug']['SQL'])
metadata = MetaData(bind=engine)

# suppress warnings concerning postgresql-specific types and indexes
warnings.simplefilter('ignore', SAWarning)

# reflect all the required schemas
metadata.reflect(schema='credo', only=lambda t,m: t in config['schema']['credo']['reflect'])
metadata.reflect(schema='pdbchem', only=lambda t,m: t in config['schema']['pdbchem']['reflect'])
metadata.reflect(schema='pdb', only=lambda t,m: t in config['schema']['pdb']['reflect'])
metadata.reflect(schema='variations', only=lambda t,m: t in config['schema']['variations']['reflect'])

# database session
Session = scoped_session(sessionmaker(bind=engine, autocommit=True))

# import Base here because the module imports the Session object
from credoscript.mixins import Base

# the declarative base that is used for all credo entities
Base = declarative_base(bind=engine, metadata=metadata, cls=Base)

# do not map against class
interface_residues = metadata.tables['credo.interface_residues']
groove_residues = metadata.tables['credo.groove_residues']
prot_fragment_residues = metadata.tables['credo.prot_fragment_residues']
chem_comp_fragment_atoms = metadata.tables['pdbchem.chem_comp_fragment_atoms']
ligand_fcd = metadata.tables['credo.ligand_fcd']
citations = metadata.tables['pdb.citations']
disordered_regions = metadata.tables['pdb.disordered_regions']
residue_interaction_pairs = metadata.tables['credo.residue_interaction_pairs']
phenotype_to_chain = metadata.tables['variations.phenotype_to_chain']
phenotype_to_ligand = metadata.tables['variations.phenotype_to_ligand']
phenotype_to_interface = metadata.tables['variations.phenotype_to_interface']
phenotype_to_groove = metadata.tables['variations.phenotype_to_groove']
variation_to_binding_site = metadata.tables['variations.variation_to_binding_site']
variation_to_interface = metadata.tables['variations.variation_to_interface']

try:
    from rdkit import Chem
    config['extras']['rdkit'] = True
except ImportError:
    pass
