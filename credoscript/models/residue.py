from sqlalchemy.ext.hybrid import hybrid_method

from credoscript import Base
from credoscript.mixins import PathMixin, ResidueMixin

class Residue(Base, PathMixin, ResidueMixin):
    """
    Represents a PDB Residue of ANY type.

    Attributes
    ----------
    residue_id : int
        Primary key.
    chain_id : int
        "Foreign key" of the parent Chain.
    res_name : str
        The PDB three-letter chemical component name / Three-letter amino acid code.
    one_letter_code : string
        The one-letter code of this amino acid.
    res_num : int
        The PDB residue number.
    ins_code : str
        The PDB insertion code.
    entity_type_bm : int
        Entity type bitmask containing six bits.

    Mapped attributes
    -----------------
    Rings : Query
        AromaticRings of this Residue in case is it aromatic.
    Atoms : Query
        Atoms of this Residue.
    XRefs : Query
        CREDO XRef objects that are associated with this Residue Entity.

    Notes
    -----
    The __getitem__ method is overloaded to allow accessing Atoms directly by
    their names, e.g. Residue['CA']. Returns a list due to atoms with
    possible alternate locations.
    """
    __tablename__ = 'credo.residues'

    @property
    def Contacts(self):
        """
        """
        adaptor = ContactAdaptor(dynamic=True)
        return adaptor.fetch_all_by_residue_id(self.residue_id,
                                               self.biomolecule_id)

    @property
    def ProximalWater(self):
        """
        Returns all water atoms that are in contact with this residue.

        Parameters
        ----------
        *expr : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried entities
        ----------------
        Subquery (not exposed), Atom

        Returns
        -------
        atoms : list
            List of `Atom` objects.

        Examples
        --------
        >>>
        """
        adaptor = AtomAdaptor(dynamic=True)
        return adaptor.fetch_all_water_in_contact_with_residue_id(self.residue_id,
                                                                  self.biomolecule_id)

    @property
    def ProximalLigands(self):
        """
        """
        adaptor = LigandAdaptor(dynamic=True)
        return adaptor.fetch_all_in_contact_with_residue_id(self.residue_id,
                                                            dynamic=True)

    @hybrid_method
    @property
    def is_polymer(self):
        """
        Returns true if the residue belongs to a polymer, i.e. polypeptide,
        oligonucleotide or polysaccharide.
        """
        return self.entity_type_bm > 2

    @is_polymer.expression
    @property
    def is_polymer(self):
        """
        Returns true if the residue belongs to a polymer, i.e. polypeptide,
        oligonucleotide or polysaccharide.
        """
        return Residue.entity_type_bm > 2

    @hybrid_method
    @property
    def is_peptide(self):
        """
        Returns true if the residue belongs to a  polypeptide.
        """
        return self.entity_type_bm == 32

    @is_peptide.expression
    @property
    def is_peptide(self):
        """
        Returns true if the residue belongs to polypeptide.
        """
        return Residue.entity_type_bm.op('&')(32) > 0

    @hybrid_method
    @property
    def is_nucleotide(self):
        """
        Returns true if the residue belongs to a oligonucleotide.
        """
        return self.entity_type_bm & 24 > 0

    @is_nucleotide.expression
    @property
    def is_nucleotide(self):
        """
        Returns true if the residue belongs to oligonucleotide.
        """
        return Residue.entity_type_bm.op('&')(24) > 0

    def sift(self, *expr):
        """
        Returns the sum of all the contact types of all the contacts this residue
        has as a tuple.

        Queried entities
        ----------------
        Residue, Atom, Contact

        Returns
        -------
        sift : tuple
            sum of all the contact types of all contacts this residue has.
        """
        return SIFtAdaptor().fetch_by_residue_id(self.ligand_id,
                                                 self.biomolecule_id,
                                                 *expr)

from ..adaptors.atomadaptor import AtomAdaptor
from ..adaptors.contactadaptor import ContactAdaptor
from ..adaptors.ligandadaptor import LigandAdaptor
from ..adaptors.siftadaptor import SIFtAdaptor
