from sqlalchemy import select
from sqlalchemy.orm import backref, deferred, relationship
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.sql.expression import and_, cast, func, text
from sqlalchemy.dialects.postgresql import INTEGER

from credoscript import Base, Session, disordered_regions
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
    __table__ = Base.metadata.tables['credo.chains']

    Residues = relationship("Residue",
                            primaryjoin="Residue.chain_id==Chain.chain_id",
                            foreign_keys="[Residue.chain_id]",
                            uselist=True, innerjoin=True, lazy='dynamic',
                            backref=backref('Chain', uselist=False, innerjoin=True))

    ResidueMap = relationship("Residue",
                              collection_class=attribute_mapped_collection("_res_num_ins_code_tuple"),
                              primaryjoin="Residue.chain_id==Chain.chain_id",
                              foreign_keys="[Residue.chain_id]",
                              uselist=True, innerjoin=True, lazy=True)

    Peptides = relationship("Peptide",
                            collection_class=attribute_mapped_collection("_res_num_ins_code_tuple"),
                            primaryjoin="Peptide.chain_id==Chain.chain_id",
                            foreign_keys="[Peptide.chain_id]",
                            uselist=True, innerjoin=True,  lazy='dynamic',
                            backref=backref('Chain', uselist=False, innerjoin=True))

    Nucleotides = relationship("Nucleotide",
                               collection_class=attribute_mapped_collection("_res_num_ins_code_tuple"),
                               primaryjoin="Nucleotide.chain_id==Chain.chain_id",
                               foreign_keys="[Nucleotide.chain_id]",
                               uselist=True, innerjoin=True,  lazy='dynamic',
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

    # DEFERRED COLUMNS
    title = deferred(__table__.c.title)
    seq = deferred(__table__.c.chain_seq)
    seq_md5 = deferred(__table__.c.chain_seq_md5)

    def __repr__(self):
        """
        """
        return '<Chain({self.pdb_chain_id})>'.format(self=self)

    def __getitem__(self, res_name, ins_code=' '):
        """
        """
        return self.ResidueMap.get(res_name, ins_code)

    def __getslice__(self, m, n):
        """
        Returns a slice containing the residues within the residue number range.
        """
        # CHANGE
        return [self.ResidueMap.get(i) for i in range(m,n+1) if i]

    def __iter__(self):
        """
        """
        return iter(self.Residues.all())

    @property
    def Variations(self):
        """
        """
        return VariationAdaptor().fetch_all_by_chain_id(self.chain_id, dynamic=True)

    @property
    def Contacts(self):
        """
        """
        return ContactAdaptor().fetch_all_by_chain_id(self.chain_id,
                                                      self.biomolecule_id,
                                                      dynamic=True)

    @property
    def ProximalLigands(self):
        """
        """
        return LigandAdaptor().fetch_all_in_contact_with_chain_id(self.chain_id,
                                                                  dynamic=True)

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

        session.close()

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

from .contact import Contact
from .atom import Atom
from .residue import Residue
from ..adaptors.peptideadaptor import PeptideAdaptor
from ..adaptors.contactadaptor import ContactAdaptor
from ..adaptors.variationadaptor import VariationAdaptor
from ..adaptors.ligandadaptor import LigandAdaptor
from ..adaptors.siftadaptor import SIFtAdaptor