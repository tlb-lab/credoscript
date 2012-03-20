import os
import json
import warnings

import psycopg2
from sqlalchemy import create_engine, MetaData
from sqlalchemy.exc import SAWarning
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# register new data types
import credoscript.util.psycopg2

# the following modules will be imported with from credoscript import *
__all__ = ['adaptors','contrib','extensions','models']

# configuration
CONFIG_PATH = os.path.join(__path__[0], 'config.json')

# exit if the configuration file does not exist
if not os.path.exists(CONFIG_PATH):
    raise IOError("""cannot find the configuration file config.json in credoscript
                  directory. Did you rename config-default.json to config.json?""")

config = json.loads(open(CONFIG_PATH).read())

# database connection
execution_options = dict(stream_results=config['connection']['stream_results'])

url      = '{driver}://{user}:{passwd}@{host}:{port}/{db}'.format(**config['connection'])
engine   = create_engine(url, echo=config['debug']['SQL'], execution_options=execution_options)

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
binding_sites = metadata.tables['credo.binding_sites']
binding_site_fuzcav = metadata.tables['credo.binding_site_fuzcav']
interface_residues = metadata.tables['credo.interface_residues']
binding_site_atom_surface_areas = metadata.tables['credo.binding_site_atom_surface_areas']
chem_comp_fragment_atoms = metadata.tables['pdbchem.chem_comp_fragment_atoms']
ligand_usr = metadata.tables['credo.ligand_usr']
ligand_fcd = metadata.tables['credo.ligand_fcd']
citations = metadata.tables['pdb.citations']
disordered_regions = metadata.tables['pdb.disordered_regions']