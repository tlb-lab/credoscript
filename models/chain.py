from sqlalchemy import select
from sqlalchemy.sql.expression import and_

from ..meta import session, disordered_regions
from .model import Model

class Chain(Model):
    '''
    Represents a `Chain` entity from CREDO.

    Attributes
    ----------
    chain_id : int
        Primary key.
    biomolecule_id : int
        Primary key of the parent Biomolecule.
    pdb_chain_id : str
        PDB chain identifier.
    pdb_chain_asu_id : str
        The PDB chain identifier this chain originated from.
    title : str
        A description of the Chain, with the name of the Chain in parenthesis.
        Maps to PDB compound name (entity.pdbx_description).
    chain_type : str

    chain_length : int
        Number of residues in the polymer chain.
    chain_seq : str
        Sequence of the polymer.
    is_at_identity : bool
        True if the chain is at identity, i.e. no transformation was performed.
    has_disordered_regions : bool
        True if the chain contains at least one residue that could not be observed
        in the electron density else false.

    Mapped attributes
    -----------------
    Residues : dict
        List of all `Residue` objects in this Chain.
    XRefs : list
        A list of cross references that are associated with this `Chain`.

    See Also
    --------
    ChainAdaptor : Fetch Chains from the database.

    Notes
    -----
    - The __getitem__ method is overloaded to allow fetching a residue by its
      residue number with Chain[123]. Returns a list in cases where residues have
      insertion codes.
    '''
    def __repr__(self):
        '''
        '''
        return '<Chain({self.pdb_chain_id})>'.format(self=self)

    def __getitem__(self, res):
        '''
        '''
        # ONLY RESIDUE NUMBER IS PROVIDED / WILL TREAT INSERTION CODE AS BLANK
        if isinstance(res, int): return self.Residues.get((res, ' '))

        # INSERTION CODE WAS PROVIDED AS WELL
        elif isinstance(res, tuple): return self.Residues.get(res)

    def __getslice__(self, m, n):
        '''
        Returns a slice containing the residues within the residue number range.
        '''
        # CHANGE
        return [self.Residues.get(i) for i in range(m,n+1) if i]

    def __iter__(self):
        '''
        '''
        return iter(self.Residues.values())

    def get_peptides(self, *expressions):
        '''
        '''
        return PeptideAdaptor().fetch_all_by_chain_id(self.chain_id, *expressions)

    def get_nucleotides(self, *expressions):
        '''
        '''
        pass
    
    def get_disordered_regions(self, *expressions):
        '''
        Returns a list of disordered regions inside this Chain (if any).
        '''
        statement = select([disordered_regions],
            and_(disordered_regions.c.pdb==self.Biomolecule.Structure.pdb,
                 disordered_regions.c.pdb_chain_id==self.pdb_chain_id_asu,
                 *expressions))

        return session.execute(statement).fetchall()

from ..adaptors.peptideadaptor import PeptideAdaptor