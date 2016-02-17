import sqlalchemy.types as types

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import BYTEA

try:
    from rdkit.Chem import Mol
except ImportError:
    RDMol = BYTEA
else:
    class RDMol(types.TypeDecorator):
        """Custom type for RDKit Molecule type""" 
        impl = BYTEA

        def get_col_spec(self):
            return "rdkit.mol"

        def process_bind_param(self, value, dialect):
            if value is not None:
                value = value.ToBinary()
            return value
            
        def bind_expression(self, bind_value):
            return func.rdkit.mol_from_pkl(bind_value)

        def process_result_value(self, value, dialect):
            #print "Processing result value", value #, type(cPickle.loads(value))
            return Mol(str(value)) if value is not None else value
            
        def column_expression(self, col):
            return func.rdkit.mol_to_pkl(col, type_=self)
