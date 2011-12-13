from sqlalchemy import select
from sqlalchemy.orm import backref, deferred, relationship
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.sql.expression import and_, cast, func, text
from sqlalchemy.dialects.postgresql import INTEGER

from credoscript import Base, session, disordered_regions

class Chain(Base):
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
    __table__ = Base.metadata.tables['credo.chains']
    
    Residues = relationship("Residue",
                            collection_class=attribute_mapped_collection("full_name"),
                            primaryjoin="Residue.chain_id==Chain.chain_id",
                            foreign_keys="[Residue.chain_id]",
                            uselist=True, innerjoin=True,
                            backref=backref('Chain', uselist=False, innerjoin=True))
    
    Peptides = relationship("Peptide",
                            collection_class=attribute_mapped_collection("full_name"),
                            primaryjoin="Peptide.chain_id==Chain.chain_id",
                            foreign_keys="[Peptide.chain_id]",
                            uselist=True, innerjoin=True,
                            backref=backref('Chain', uselist=False, innerjoin=True))
        
    ProtFragments = relationship("ProtFragment",
                                 primaryjoin="ProtFragment.chain_id==Chain.chain_id",
                                 foreign_keys="[ProtFragment.chain_id]",
                                 uselist=True, innerjoin=True,
                                 backref=backref('Chain', uselist=False, innerjoin=True))
    
    XRefs = relationship("XRef",
                         collection_class=attribute_mapped_collection("source"),
                         primaryjoin="and_(XRef.entity_type=='Chain', XRef.entity_id==Chain.chain_id)",
                         foreign_keys="[XRef.entity_type, XRef.entity_id]", uselist=True, innerjoin=True),
      
    # DEFERRED COLUMNS  
    title = deferred(__table__.c.title)
    seq = deferred(__table__.c.chain_seq)
    seq_md5 = deferred(__table__.c.chain_seq_md5)    
    
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

    def get_residue_sifts(self, *expressions):
        '''
        Returns all polymer residues of this chain and their summed structural
        interaction fingerprint (SIFt). Only intermolecular contacts are considered
        and secondary contacts are ignored.
        
        Parameters
        ----------
        *expressions : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.
        
        Returns
        -------
        sift : list
            list of lists in the form [(Residue, SIFt),...].
        
        Examples
        --------
        >>> structure = StructureAdaptor().fetch_by_pdb('2p33')
        >>> chain = structure[0]['A']
        >>> chain.get_residue_sifts(Contact.structural_interaction_type=PRO_LIG)
        >>> [(<Residue(ILE 70 )>, 0L, 0L, 0L, 25L, 0L, 1L, 0L, 0L, 0L, 0L, 2L, 0L),
             (<Residue(GLY 71 )>, 0L, 0L, 0L, 4L, 0L, 0L, 0L, 0L, 0L, 0L, 0L, 0L),
             (<Residue(SER 72 )>, 0L, 0L, 0L, 3L, 0L, 1L, 0L, 0L, 0L, 0L, 0L, 0L),...]
        '''
        query = session.query(Residue.residue_id.label('residue_id'), Contact).select_from(Contact)

        whereclause = and_(Residue.chain_id==self.chain_id,
                           Contact.biomolecule_id==self.biomolecule_id,
                           Contact.is_same_entity==False,
                           Contact.is_secondary==False,
                           *expressions)

        bgn = query.join(Atom, and_(Atom.atom_id==Contact.atom_bgn_id,
                                    Atom.biomolecule_id==Contact.biomolecule_id)
                         ).join(Residue, Residue.residue_id==Atom.residue_id).filter(whereclause)
        
        end = query.join(Atom, and_(Atom.atom_id==Contact.atom_end_id,
                                    Atom.biomolecule_id==Contact.biomolecule_id)
                         ).join(Residue, Residue.residue_id==Atom.residue_id).filter(whereclause)
        
        subquery = bgn.union(end).subquery()
        
        # RESIDUE ID AND SUM OF STRUCTURAL INTERACTION FINGERPRINTS
        fields = (subquery.c.residue_id,
                  func.sum(cast(subquery.c.credo_contacts_is_covalent, INTEGER)).label('is_covalent'),
                  func.sum(cast(subquery.c.credo_contacts_is_vdw_clash, INTEGER)).label('is_vdw_clash'),
                  func.sum(cast(subquery.c.credo_contacts_is_vdw, INTEGER)).label('is_vdw'),
                  func.sum(cast(subquery.c.credo_contacts_is_proximal, INTEGER)).label('is_proximal'),
                  func.sum(cast(subquery.c.credo_contacts_is_hbond, INTEGER)).label('is_hbond'),
                  func.sum(cast(subquery.c.credo_contacts_is_weak_hbond, INTEGER)).label('is_weak_hbond'),
                  func.sum(cast(subquery.c.credo_contacts_is_xbond, INTEGER)).label('is_xbond'),
                  func.sum(cast(subquery.c.credo_contacts_is_ionic, INTEGER)).label('is_ionic'),
                  func.sum(cast(subquery.c.credo_contacts_is_metal_complex, INTEGER)).label('is_metal_complex'),
                  func.sum(cast(subquery.c.credo_contacts_is_aromatic, INTEGER)).label('is_aromatic'),
                  func.sum(cast(subquery.c.credo_contacts_is_hydrophobic, INTEGER)).label('is_hydrophobic'),
                  func.sum(cast(subquery.c.credo_contacts_is_carbonyl, INTEGER)).label('is_carbonyl'))

        # AGGREGATE TO GET THE SUM
        sift = session.query(*fields).group_by('residue_id').order_by('residue_id').subquery()
 
        # INCLUDE THE RESIDUE OBJECT IN RESULT SET
        query = session.query(Residue, sift.c.is_covalent, sift.c.is_vdw_clash,
                              sift.c.is_vdw, sift.c.is_proximal, sift.c.is_hbond,
                              sift.c.is_weak_hbond, sift.c.is_xbond, sift.c.is_ionic,
                              sift.c.is_metal_complex, sift.c.is_aromatic, sift.c.is_hydrophobic,
                              sift.c.is_carbonyl)
        
        query = query.join(sift, sift.c.residue_id==Residue.residue_id)
        
        return query.all()
  
from .contact import Contact
from .atom import Atom
from .residue import Residue
from ..adaptors.peptideadaptor import PeptideAdaptor
from ..adaptors.contactadaptor import ContactAdaptor