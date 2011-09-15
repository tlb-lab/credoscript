from sqlalchemy import select
from sqlalchemy.sql.expression import and_, text
from sqlalchemy.dialects.postgresql import INTEGER

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
    
    def get_contacts(self, *expressions):
        '''
        '''
        return ContactAdaptor().fetch_all_by_chain_id(self.chain_id, *expressions)
    
    def get_disordered_regions(self, *expressions):
        '''
        Returns a list of disordered regions inside this Chain (if any).
        '''
        statement = select([disordered_regions],
            and_(disordered_regions.c.pdb==self.Biomolecule.Structure.pdb,
                 disordered_regions.c.pdb_chain_id==self.pdb_chain_asu_id,
                 *expressions))

        return session.execute(statement).fetchall()

    def get_residue_sifts(self, structural_interaction_type):
        '''
        Returns all polymer residues of this chain and their summed structural
        interaction fingerprint (SIFt). Only intermolecular contacts are considered
        and secondary contacts are ignored.
        
        Parameters
        ----------
        structural_interaction_type : int
            CREDO structural interaction type (e.g. PRO_LIG) that will be used
            to filter the SIFts.
        
        Returns
        -------
        sift : list
            list of lists in the form [(Residue, sift),...].
        
        Examples
        --------
        >>> structure = StructureAdaptor().fetch_by_pdb('2p33')
        >>> chain = structure[0]['A']
        >>> chain.get_residue_sifts(structural_interaction_type=PRO_LIG)
        >>> [(<Residue(ILE 70 )>, 0L, 0L, 0L, 25L, 0L, 1L, 0L, 0L, 0L, 0L, 2L, 0L),
             (<Residue(GLY 71 )>, 0L, 0L, 0L, 4L, 0L, 0L, 0L, 0L, 0L, 0L, 0L, 0L),
             (<Residue(SER 72 )>, 0L, 0L, 0L, 3L, 0L, 1L, 0L, 0L, 0L, 0L, 0L, 0L),...]
        '''
        statement = text('''
                        SELECT  sq.residue_id,
                                sum(sq.is_covalent::int) as is_covalent,
                                sum(sq.is_vdw_clash::int) as is_vdw_clash,
                                sum(sq.is_vdw::int) as is_vdw,
                                sum(sq.is_proximal::int) as is_proximal,
                                sum(sq.is_hbond::int) as is_hbond,
                                sum(sq.is_weak_hbond::int) as is_weak_hbond,
                                sum(sq.is_xbond::int) as is_xbond,
                                sum(sq.is_ionic::int) as is_ionic,
                                sum(sq.is_metal_complex::int) as is_metal_complex,
                                sum(sq.is_aromatic::int) as is_aromatic,
                                sum(sq.is_hydrophobic::int) as is_hydrophobic,
                                sum(sq.is_carbonyl::int) as is_carbonyl
                        FROM    (
                                SELECT  r.*, cs.*
                                FROM    credo.contacts cs
                                JOIN    credo.atoms a ON a.atom_id = cs.atom_bgn_id
                                JOIN    credo.residues r ON r.residue_id = a.residue_id
                                WHERE   cs.is_same_entity = false
                                        AND cs.is_secondary = false
                                        AND r.entity_type_bm > 2 
                                        AND r.chain_id = :chain_id
                                        AND cs.structural_interaction_type = :structural_interaction_type
                                UNION
                                SELECT  r.*, cs.*
                                FROM    credo.contacts cs
                                JOIN    credo.atoms a ON a.atom_id = cs.atom_end_id
                                JOIN    credo.residues r ON r.residue_id = a.residue_id
                                WHERE   cs.is_same_entity = false
                                        AND cs.is_secondary = false
                                        AND r.entity_type_bm > 2 
                                        AND r.chain_id = :chain_id
                                        AND cs.structural_interaction_type = :structural_interaction_type
                                ) sq
                        GROUP BY sq.residue_id
                        ORDER BY sq.residue_id
                         ''')
        
        params = {'chain_id': self.chain_id,
                  'structural_interaction_type': structural_interaction_type}
        
        query = session.query(Residue,'is_covalent','is_vdw_clash','is_vdw','is_proximal',
                              'is_hbond','is_weak_hbond','is_xbond','is_ionic',
                              'is_metal_complex','is_aromatic','is_hydrophobic',
                              'is_carbonyl')
        
        query = query.from_statement(statement)
        query = query.params(**params)
        
        return query.all()

from .residue import Residue
from ..adaptors.peptideadaptor import PeptideAdaptor
from ..adaptors.contactadaptor import ContactAdaptor