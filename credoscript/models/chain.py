from sqlalchemy import select
from sqlalchemy.orm import backref, deferred, relationship
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.sql.expression import and_

from credoscript import Base, schema, Session, disordered_regions
from credoscript.mixins import PathMixin

class Chain(Base, PathMixin):
    """
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
    """
    __table__ = Base.metadata.tables['%s.chains' % schema['credo']]

    Residues = relationship("Residue",
                            primaryjoin="Residue.chain_id==Chain.chain_id",
                            foreign_keys="[Residue.chain_id]",
                            uselist=True, innerjoin=True, lazy='dynamic',
                            backref=backref('Chain', uselist=False, innerjoin=True))

    ResidueMap = relationship("Residue",
                              collection_class=attribute_mapped_collection("_res_num_ins_code_tuple"),
                              primaryjoin="Residue.chain_id==Chain.chain_id",
                              foreign_keys="[Residue.chain_id]",
                              uselist=True, innerjoin=True)

    Peptides = relationship("Peptide",
                            collection_class=attribute_mapped_collection("_res_num_ins_code_tuple"),
                            primaryjoin="Peptide.chain_id==Chain.chain_id",
                            foreign_keys="[Peptide.chain_id]",
                            uselist=True, innerjoin=True,  lazy='dynamic',
                            backref=backref('Chain', uselist=False, innerjoin=True))

    PeptideMap = relationship("Peptide",
                              collection_class=attribute_mapped_collection("_res_num_ins_code_tuple"),
                              primaryjoin="Peptide.chain_id==Chain.chain_id",
                              foreign_keys="[Peptide.chain_id]",
                              uselist=True, innerjoin=True)

    Nucleotides = relationship("Nucleotide",
                               collection_class=attribute_mapped_collection("_res_num_ins_code_tuple"),
                               primaryjoin="Nucleotide.chain_id==Chain.chain_id",
                               foreign_keys="[Nucleotide.chain_id]",
                               uselist=True, innerjoin=True,  lazy='dynamic',
                               backref=backref('Chain', uselist=False, innerjoin=True))

    Polypeptide = relationship("Polypeptide",
                               primaryjoin="Polypeptide.chain_id==Chain.chain_id",
                               foreign_keys="[Polypeptide.chain_id]",
                               uselist=False, innerjoin=True,
                               backref=backref('Chain', uselist=False, innerjoin=True))

    Oligonucleotide = relationship("Oligonucleotide",
                                   primaryjoin="Oligonucleotide.chain_id==Chain.chain_id",
                                   foreign_keys="[Oligonucleotide.chain_id]",
                                   uselist=False, innerjoin=True,
                                   backref=backref('Chain', uselist=False, innerjoin=True))

    ProtFragments = relationship("ProtFragment",
                                 primaryjoin="ProtFragment.chain_id==Chain.chain_id",
                                 foreign_keys="[ProtFragment.chain_id]",
                                 uselist=True, innerjoin=True,  lazy='dynamic',
                                 backref=backref('Chain', uselist=False, innerjoin=True))

    XRefs = relationship("XRef",
                         primaryjoin="and_(XRef.entity_type=='Chain', XRef.entity_id==Chain.chain_id)",
                         foreign_keys="[XRef.entity_type, XRef.entity_id]",
                         lazy='dynamic', uselist=True, innerjoin=True)

    XRefMap = relationship("XRef",
                           collection_class=attribute_mapped_collection("source"),
                           primaryjoin="and_(XRef.entity_type=='Chain', XRef.entity_id==Chain.chain_id)",
                           foreign_keys="[XRef.entity_type, XRef.entity_id]",
                           uselist=True, innerjoin=True)

    # deferred columns
    title = deferred(__table__.c.title)
    seq = deferred(__table__.c.chain_seq)
    seq_md5 = deferred(__table__.c.chain_seq_md5)

    def __repr__(self):
        """
        """
        return '<Chain({self.path})>'.format(self=self)

    def __getitem__(self, t):
        """
        """
        if not isinstance(t, tuple): t = (t, ' ')
        return self.ResidueMap.get(t)

    def __getslice__(self, m, n):
        """
        Returns a slice containing the residues within the residue number range.
        """
        # CHANGE
        return [self.ResidueMap.get(i) for i in range(m, n+1) if i]

    def __iter__(self):
        """
        """
        return iter(self.Residues.all())

    @property
    def Domains(self):
        """
        """
        adaptor = DomainAdaptor(dynamic=True)
        return adaptor.fetch_all_by_chain_id(self.chain_id)

    @property
    def Variations(self):
        """
        """
        adaptor = VariationAdaptor(dynamic=True)
        return adaptor.fetch_all_by_chain_id(self.chain_id)

    @property
    def Contacts(self):
        """
        """
        adaptor = ContactAdaptor(dynamic=True)
        return adaptor.fetch_all_by_chain_id(self.chain_id, self.biomolecule_id)

    @property
    def ProximalLigands(self):
        """
        """
        adaptor = LigandAdaptor(dynamic=True)
        return adaptor.fetch_all_in_contact_with_chain_id(self.chain_id)

    def disordered_regions(self, *expr):
        """
        Returns a list of disordered regions inside this Chain (if any).
        """
        session = Session()

        statement = select([disordered_regions],
            and_(disordered_regions.c.pdb==self.Biomolecule.Structure.pdb,
                 disordered_regions.c.pdb_chain_id==self.pdb_chain_asu_id,
                 *expr))

        result = session.execute(statement).fetchall()

        return result

    def residue_sift(self, *expr):
        """
        Returns all polymer residues of THIS chain and their summed structural
        interaction fingerprint (SIFt). Only intermolecular contacts are considered.

        Parameters
        ----------
        *expr : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Returns
        -------
        sift : list
            list of lists in the form [(Residue, SIFt),...].

        Examples
        --------
        >>> structure = StructureAdaptor().fetch_by_pdb('2p33')
        >>> chain = structure[0]['A']
        >>> chain.residue_sifts()
        >>> [(<Residue(ILE 70 )>, 0L, 0L, 0L, 25L, 0L, 1L, 0L, 0L, 0L, 0L, 2L, 0L),
             (<Residue(GLY 71 )>, 0L, 0L, 0L, 4L, 0L, 0L, 0L, 0L, 0L, 0L, 0L, 0L),
             (<Residue(SER 72 )>, 0L, 0L, 0L, 3L, 0L, 1L, 0L, 0L, 0L, 0L, 0L, 0L),...]
        """
        return SIFtAdaptor().fetch_by_own_chain_id(self.chain_id, self.biomolecule_id,
                                                   *expr)

class Polypeptide(Base):
    """
    """
    __table__ = Base.metadata.tables['%s.polypeptides' % schema['credo']]

class Oligonucleotide(Base):
    """
    """
    __table__ = Base.metadata.tables['%s.oligonucleotides' % schema['credo']]

from ..adaptors.contactadaptor import ContactAdaptor
from ..adaptors.domainadaptor import DomainAdaptor
from ..adaptors.variationadaptor import VariationAdaptor
from ..adaptors.ligandadaptor import LigandAdaptor
from ..adaptors.siftadaptor import SIFtAdaptor
