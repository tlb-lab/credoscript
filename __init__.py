import os
import json
import warnings

from sqlalchemy import create_engine, MetaData
from sqlalchemy.exc import SAWarning
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from credoscript.mixins import Base

# THE FOLLOWING MODULES WILL BE IMPORTED WITH FROM CREDOSCRIPT IMPORT *
__all__ = ['adaptors','contrib','extensions','models']

# CONFIGURATION
CONFIG_PATH = os.path.join(__path__[0], 'config.json')

# EXIT IF THE CONFIGURATION FILE DOES NOT EXIST
if not os.path.exists(CONFIG_PATH):
    raise IOError("""cannot find the configuration file config.json in credoscript
                  directory. Did you rename config-default.json to config.json?""")

config = json.loads(open(CONFIG_PATH).read())

# DATABASE CONNECTION
url      = '{driver}://{user}:{passwd}@{host}:{port}/{db}'.format(**config['connection'])
engine   = create_engine(url, echo=config['debug']['SQL'])
metadata = MetaData(bind=engine)

# SUPPRESS WARNINGS CONCERNING POSTGRESQL-SPECIFIC TYPES AND INDEXES
warnings.simplefilter('ignore', SAWarning)

# REFLECT ALL THE REQUIRED SCHEMAS
metadata.reflect(schema='credo')
metadata.reflect(schema='pdbchem')
metadata.reflect(schema='pdb')

# THE DECLARATIVE BASE THAT IS USED FOR ALL CREDO ENTITIES
Base = declarative_base(bind=engine, metadata=metadata, cls=Base)

# DATABASE SESSION
Session = sessionmaker(bind=engine, autocommit=True)
session = Session()

# DO NOT MAP AGAINST CLASS
binding_sites = metadata.tables['credo.binding_sites']
interface_residues = metadata.tables['credo.interface_residues']
binding_site_atom_surface_areas = metadata.tables['credo.binding_site_atom_surface_areas']
chem_comp_fragment_atoms = metadata.tables['pdbchem.chem_comp_fragment_atoms']
ligand_usr = metadata.tables['credo.ligand_usr']
citations = metadata.tables['pdb.citations']
disordered_regions = metadata.tables['pdb.disordered_regions']