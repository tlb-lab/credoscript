import os
import json
import warnings

from sqlalchemy import create_engine, MetaData, event, exc
from sqlalchemy.pool import Pool, NullPool, SingletonThreadPool, QueuePool
from sqlalchemy.exc import SAWarning
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base

# register new data types
import credoscript.util.psycopg2

# credoscript version number scheme: year, month, release
# based on the database release
__version_info__ = (2015, 6, 1)
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


@event.listens_for(Pool, "checkout")
def ping_connection(dbapi_connection, connection_record, connection_proxy):
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("SELECT 1")
    except Exception:
        # optional - dispose the whole pool
        # instead of invalidating one at a time
        connection_proxy._pool.dispose()

        # raise DisconnectionError - pool will try
        # connecting again up to three times before raising.
        #raise exc.DisconnectionError()
    cursor.close()

pool_map = {'null': NullPool, 'singleton': SingletonThreadPool, 'queue': QueuePool}

pool_kwargs = {'poolclass': pool_map.get(config['connection'].pop('poolclass', 'queue')),
               'pool_recycle': config['connection'].pop('pool_recycle', 300)}
if pool_kwargs['poolclass'] is not NullPool:
    pool_kwargs['pool_size'] = config['connection'].pop('pool_size', 5)

url      = URL(**config['connection'])
engine   = create_engine(url, echo=config['debug']['SQL'],
                         connect_args={'sslmode': 'disable'},
                         **pool_kwargs)
metadata = MetaData(bind=engine)

# suppress warnings concerning postgresql-specific types and indexes
warnings.simplefilter('ignore', SAWarning)

schema = {}
schema['credo'] = config['schema']['credo']['name']
schema['pdbchem'] = config['schema']['pdbchem']['name']
schema['pdb'] = config['schema']['pdb']['name']
schema['variations'] = config['schema']['variations']['name']


# reflect all the required schemas
metadata.reflect(schema=schema['credo'], only=lambda t,m: t in config['schema']['credo']['reflect'])
metadata.reflect(schema=schema['pdbchem'], only=lambda t,m: t in config['schema']['pdbchem']['reflect'])
metadata.reflect(schema=schema['pdb'], only=lambda t,m: t in config['schema']['pdb']['reflect'])
metadata.reflect(schema=schema['variations'], only=lambda t,m: t in config['schema']['variations']['reflect'])

# database session
Session = scoped_session(sessionmaker(bind=engine)) #, autocommit=True)) 
# BO: Autocommit True leads to some settings (like similarity thresholds) not applying to a query;
# Adrian had it on for some reason, despite not being the "recommended" settings, probably to avoid accumulation
# of open connections.
# OK, I may know why AS had it set: the web interface sometimes leads to transactions getting somehow aborted
# and since they don't get rolled back, commands get ignored. Autocommit disables transactions, so this stops being an issue.
# This ought to be properly dealt with on the web interface, though.

# import Base here because the module imports the Session object
from credoscript.mixins import Base, BaseQuery

# the declarative base that is used for all credo entities
Base = declarative_base(bind=engine, metadata=metadata, cls=Base)

# To be joined for mapping
pi_groups   = metadata.tables['%s.pi_groups' % schema['credo']]
pi_residues = metadata.tables['%s.pi_group_residues' % schema['credo']]

# do not map against class
prot_fragment_residues = metadata.tables['%s.prot_fragment_residues' % schema['credo']]
chem_comp_fragment_atoms = metadata.tables['%s.chem_comp_fragment_atoms' % schema['pdbchem']]
citations = metadata.tables['%s.citations' % schema['pdb']]
disordered_regions = metadata.tables['%s.disordered_regions' % schema['pdb']]
residue_interaction_pairs = metadata.tables['%s.residue_interaction_pairs' % schema['credo']]
phenotype_to_chain = metadata.tables['%s.phenotype_to_chain' % schema['variations']]
phenotype_to_ligand = metadata.tables['%s.phenotype_to_ligand' % schema['variations']]
phenotype_to_interface = metadata.tables['%s.phenotype_to_interface' % schema['variations']]
phenotype_to_groove = metadata.tables['%s.phenotype_to_groove' % schema['variations']]
variation_to_binding_site = metadata.tables['%s.variation_to_binding_site' % schema['variations']]
variation_to_interface = metadata.tables['%s.variation_to_interface' % schema['variations']]

try:
    from rdkit import Chem
    config['extras']['rdkit'] = True
except ImportError:
    if config['extras']['rdkit']:
        warnings.warn("Failed to import RDKit package", UserWarning)
        config['extras']['rdkit'] = False
