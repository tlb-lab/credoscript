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
        return ContactAdaptor().fetch_all_by_residue_id(self.residue_id,
                                                        self.biomolecule_id,
                                                        dynamic=True)

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
        return AtomAdaptor().fetch_all_water_in_contact_with_residue_id(self.residue_id,
                                                                        self.biomolecule_id,
                                                                        dynamic=True)

    @property
    def ProximalLigands(self):
        """
        """
        return LigandAdaptor().fetch_all_in_contact_with_residue_id(self.residue_id,
                                                                    dynamic=True)

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
        return SIFtAdaptor().fetch_by_residue_id(self.ligand_id, self.biomolecule_id, *expr)

from ..adaptors.atomadaptor import AtomAdaptor
from ..adaptors.contactadaptor import ContactAdaptor
from ..adaptors.ligandadaptor import LigandAdaptor
from ..adaptors.siftadaptor import SIFtAdaptor
