from sqlalchemy.orm import reconstructor
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy.sql.expression import func

try: from rdkit.Chem import Mol, MolFromSmarts
except ImportError: pass

from credoscript import Base
from ..support import requires

class ChemCompRDMol(Base):
    '''
    This class contains the RDKit RDMol object for a chemical component from CREDO.
    Only available if the RDKit PostgreSQL cartridge is installed on the server
    and the RDKit Python wrappers are available on the client side.
    '''
    __tablename__ = 'pdbchem.chem_comp_rdmols'
    
    def __repr__(self):
        '''
        '''
        return '<ChemCompRDMol({self.het_id})>'.format(self=self)

    def __len__(self):
        '''
        Returns the number of atoms in this RDMol.

        Returns
        -------
        num_atoms : int
            Number of atoms in this RDMol.

        Notes
        -----
        - Overloads len() function.
        '''
        return self.rdmol.GetNumAtoms()

    def __contains__(self, smiles):
        '''
        Returns true if the given SMILES string is a substructure of this RDMol.

        Returns
        -------
        contains : boolean
            True if the SMILES string is a substructure of this RDMol.

        Notes
        -----
        - Overloads 'in' operator.
        '''
        return self.contains(smiles)

    def __iter__(self):
        '''
        Returns an iterator over the atoms of this RDMol.
        
        Notes
        -----
        - Overloads 'for object in instance' operator.
        '''
        return iter(self.rdmol.GetAtoms())

    @reconstructor
    @requires.rdkit
    def init_on_load(self):
        '''
        Turns the rdmol column that is returned as a SMILES string back into an
        RDMol object.
        '''
        self.rdmol = Mol(str(self.rdmol))

    @hybrid_method
    @requires.rdkit
    def contains(self, smiles):
        '''
        Returns true if the given SMILES string is a substructure of this RDMol.
        Uses a client-side RDKit installation.

        Returns
        -------
        contains : boolean
            True if the rdmol molecule attribute contains the specified substructure
            in SMILES format.
        '''
        return self.rdmol.HasSubstructMatch(MolFromSmiles(str(smiles)))

    @contains.expression
    def contains(self, smiles):
        '''
        Returns a RDKit cartridge substructure query in form of an SQLAlchemy binary
        expression.

        Returns
        -------
        expression : sqlalchemy.sql.expression._BinaryExpression
            SQL expression that can be used to query ChemCompRDMol for substructure
            hits.
        '''
        return self.rdmol.op('OPERATOR(rdkit.@>)')(smiles)

    @hybrid_method
    @requires.rdkit
    def contained_in(self, smiles):
        '''
        Returns true if the given SMILES string is a superstructure of this RDMol.
        Uses a client-side RDKit installation.

        Returns
        -------
        contains : boolean
            True if the rdmol molecule attribute is contained in the specified
            substructure in SMILES format.
        '''
        return MolFromSmiles(smiles).HasSubstructMatch(self.rdmol)

    @contained_in.expression
    def contained_in(self, smiles):
        '''
        Returns a RDKit cartridge superstructure query in form of an SQLAlchemy binary
        expression.

        Returns
        -------
        expression : sqlalchemy.sql.expression._BinaryExpression
            SQL expression that can be used to query ChemCompRDMol for superstructure
            hits.
        '''
        return self.rdmol.op('OPERATOR(rdkit.<@)')(smiles)
    
    @hybrid_method
    @requires.rdkit
    def matches(self, smarts):
        '''
        Returns true if the RDMol matches the given SMARTS query. Uses a client-side
        RDKit installation.

        Returns
        -------
        matches : boolean
            True if the rdmol molecule attribute matches the given SMARTS query.
        '''
        return self.rdmol.HasSubstructMatch(MolFromSmarts(smarts))

    @matches.expression
    def matches(self, smarts):
        '''
        Returns a SMARTS match query in form of an SQLAlchemy binary expression.

        Returns
        -------
        expression : sqlalchemy.sql.expression._BinaryExpression
            SQL expression that can be used to query ChemCompRDMol for SMARTS matches.
        '''
        return self.rdmol.op('OPERATOR(rdkit.@>)')(func.rdkit.qmol_in(smarts))