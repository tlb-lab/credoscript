from sqlalchemy import Column
from sqlalchemy.orm import reconstructor, column_property
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy.sql.expression import func

try:
    from rdkit.Chem import MolFromSmarts, MolFromSmiles
except ImportError:
    pass

from credoscript import Base, schema
from credoscript.util import requires
from credoscript.ext.rdkit_ import RDMol


frag_rdmol_table = Base.metadata.tables['%s.fragment_rdmols' % schema['pdbchem']]

class FragmentRDMol(Base):
    """
    This class contains the RDKit RDMol object for a fragment from CREDO.
    Only available if the RDKit PostgreSQL cartridge is installed on the server
    and the RDKit Python wrappers are available on the client side.
    """
    __tablename__ = '%s.fragment_rdmols' % schema['pdbchem']
    __table_args__ = {'autoload': True, 'extend_existing': True}
    
    rdmol = Column('rdmol', RDMol())
    as_smarts = column_property(func.rdkit.mol_to_smarts(frag_rdmol_table.c.rdmol), deferred=True)

    def __repr__(self):
        """
        """
        return '<FragmentRDMol({self.fragment_id})>'.format(self=self)

    @requires.rdkit
    def __len__(self):
        """
        Returns the number of atoms in this RDMol.

        Returns
        -------
        num_atoms : int
            Number of atoms in this RDMol.

        Notes
        -----
        - Overloads len() function.
        """
        return self.rdmol.GetNumAtoms()

    @requires.rdkit
    def __contains__(self, smiles):
        """
        Returns true if the given SMILES string is a substructure of this RDMol.

        Returns
        -------
        contains : boolean
            True if the SMILES string is a substructure of this RDMol.

        Notes
        -----
        - Overloads 'in' operator.
        """
        return self.contains(smiles)

    @requires.rdkit
    def __iter__(self):
        """
        Returns an iterator over the atoms of this RDMol.

        Notes
        -----
        - Overloads 'for object in instance' operator.
        """
        return iter(self.rdmol.GetAtoms())

    # @reconstructor
    # @requires.rdkit
    # def init_on_load(self):
        # """
        # Turns the rdmol column that is returned as a SMILES string back into an
        # RDMol object.
        # """
        # self.rdmol = MolFromSmiles(str(self.rdmol))

    @hybrid_method
    @requires.rdkit
    def contains(self, smiles):
        """
        Returns true if the given SMILES string is a substructure of this RDMol.
        Uses a client-side RDKit installation.

        Returns
        -------
        contains : boolean
            True if the rdmol molecule attribute contains the specified substructure
            in SMILES format.
        """
        return self.rdmol.HasSubstructMatch(MolFromSmiles(str(smiles)))

    @contains.expression
    def contains(self, smiles):
        """
        Returns a RDKit cartridge substructure query in form of an SQLAlchemy binary
        expression.

        Returns
        -------
        expression : sqlalchemy.sql.expression._BinaryExpression
            SQL expression that can be used to query FragmentRDMol for substructure
            hits.
        """
        return self.rdmol.op('OPERATOR(rdkit.@>)')(smiles)

    @hybrid_method
    @requires.rdkit
    def contained_in(self, smiles):
        """
        Returns true if the given SMILES string is a superstructure of this RDMol.
        Uses a client-side RDKit installation.

        Returns
        -------
        contains : boolean
            True if the rdmol molecule attribute is contained in the specified
            substructure in SMILES format.
        """
        return MolFromSmiles(smiles).HasSubstructMatch(self.rdmol)

    @contained_in.expression
    def contained_in(self, smiles):
        """
        Returns a RDKit cartridge superstructure query in form of an SQLAlchemy binary
        expression.

        Returns
        -------
        expression : sqlalchemy.sql.expression._BinaryExpression
            SQL expression that can be used to query FragmentRDMol for superstructure
            hits.
        """
        return self.rdmol.op('OPERATOR(rdkit.<@)')(smiles)

    @hybrid_method
    @requires.rdkit
    def matches(self, smarts):
        """
        Returns true if the RDMol matches the given SMARTS query. Uses a client-side
        RDKit installation.

        Returns
        -------
        matches : boolean
            True if the rdmol molecule attribute matches the given SMARTS query.
        """
        return self.rdmol.HasSubstructMatch(MolFromSmarts(smarts))

    @matches.expression
    def matches(self, smarts):
        """
        Returns a SMARTS match query in form of an SQLAlchemy binary expression.

        Returns
        -------
        expression : sqlalchemy.sql.expression._BinaryExpression
            SQL expression that can be used to query FragmentRDMol for SMARTS matches.
        """
        return self.rdmol.op('OPERATOR(rdkit.@>)')(func.rdkit.qmol_in(smarts))
        
try:   
    class FragmentRDFP(Base):
        '''
        '''
        __tablename__ = '%s.fragment_rdfps' % schema['pdbchem']

        def __repr__(self):
            '''
            '''
            return '<FragmentRDFP({self.fragment_id})>'.format(self=self)
except Exception:
    print "Error initialising class FragmentRDFP"