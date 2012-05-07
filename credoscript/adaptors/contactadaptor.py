from sqlalchemy.orm import aliased, joinedload
from sqlalchemy.sql.expression import and_, func

from credoscript.mixins.base import paginate

class ContactAdaptor(object):
    """
    Class to fetch interatomic contacts from CREDO. The contacts table is partitioned
    by biomolecule_id hence this column should be used to use constraint-exclusion.
    """
    def __init__(self, paginate=False, per_page=100):
        """
        """
        self.query = Contact.query
        self.paginate = paginate
        self.per_page = per_page

    def fetch_by_contact_id(self, contact_id, biomolecule_id):
        """
        Parameters
        ----------
        contact_id : int
            Primary key of the `Contact` in CREDO.
        biomolecule_id : int

        Queried Entities
        ----------------
        Contact

        Returns
        -------
        Contact
            CREDO `Contact` object having this contact_id as primary key.

        Examples
        --------
        >>> ContactAdaptor().fetch_by_contact_id(1)
        <Contact(1)>
        """
        query = self.query.filter_by(contact_id=contact_id, biomolecule_id=biomolecule_id)

        return query.first()

    @paginate
    def fetch_all_by_atom_id(self, atom_id, biomolecule_id, *expr, **kwargs):
        """
        Returns a list of `Contact` objects that form interatomic contacts with the atom.

        Parameters
        ----------
        atom_id : int
            `Atom` identifier.
        biomolecule_id : int

        *expr : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried Entities
        ----------------
        Contact

        Returns
        -------
        contacts : list
            List of `contact` objects.

         Examples
        --------
        >>> ContactAdaptor().fetch_all_by_atom_id(1)
        <Contact()>
        """
        bgn = self.query.filter(and_(Contact.atom_bgn_id==atom_id,
                                     Contact.biomolecule_id==biomolecule_id, *expr))
        end = self.query.filter(and_(Contact.atom_end_id==atom_id,
                                     Contact.biomolecule_id==biomolecule_id, *expr))

        query = bgn.union_all(end)

        return query

    @paginate
    def fetch_all_by_residue_id(self, residue_id, biomolecule_id, *expr, **kwargs):
        """
        Returns a list of `Contact` objects that form interatomic contacts with the residue.

        Parameters
        ----------
        residue_id : int
            `Residue` identifier.
        biomolecule_id : int

        *expr : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried Entities
        ----------------
        Contact, Atom

        Returns
        -------
        contacts : list
            List of `contact` objects.

         Examples
        --------
        >>> ContactAdaptor().fetch_all_by_residue_id(1)
        <Contact()>
        """
        where = and_(Atom.residue_id==residue_id,
                           Contact.biomolecule_id==biomolecule_id,
                           Atom.biomolecule_id==Contact.biomolecule_id,
                           *expr)

        bgn = self.query.join('AtomBgn').filter(where)
        end = self.query.join('AtomEnd').filter(where)

        query = bgn.union_all(end)

        return query

    @paginate
    def fetch_all_by_ligand_id(self, ligand_id, biomolecule_id, *expr, **kwargs):
        """
        Returns a list of `Contact` objects that form interatomic contacts with the atom.

        Parameters
        ----------
        ligand_id : int
            `Ligand` identifier.
        biomolecule_id : int

        *expr : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried Entities
        ----------------
        Contact, Hetatm

        Returns
        -------
        contacts : list
            List of `contact` objects.

         Examples
        --------
        >>> ContactAdaptor().fetch_all_by_ligand_id(1)
        <Contact()>
        """
        where = and_(Contact.biomolecule_id==biomolecule_id,
                     Hetatm.ligand_id==ligand_id, *expr)

        bgn = self.query.join((Hetatm, Hetatm.atom_id==Contact.atom_bgn_id))
        bgn = bgn.filter(where)

        end = self.query.join((Hetatm, Hetatm.atom_id==Contact.atom_end_id))
        end = end.filter(where)

        query = bgn.union_all(end)

        # eager-load the interacting atoms
        if kwargs.get('load_atoms'):
            query = query.options(joinedload(Contact.AtomBgn, innerjoin=True),
                                  joinedload(Contact.AtomEnd, innerjoin=True))

        return query

    @paginate
    def fetch_all_by_chain_id(self, chain_id, biomolecule_id, *expr, **kwargs):
        """
        """
        where = and_(Residue.chain_id==chain_id,
                     Contact.biomolecule_id==biomolecule_id,
                     *expr)

        bgn = self.query.join('AtomBgn','Residue').filter(where)
        end = self.query.join('AtomEnd','Residue').filter(where)

        # eager-load the interacting atoms
        if kwargs.get('load_atoms'):
            query = query.options(joinedload(Contact.AtomBgn, innerjoin=True),
                                  joinedload(Contact.AtomEnd, innerjoin=True))

        query = bgn.union(end)

        return query

    @paginate
    def fetch_all_by_interface_id(self, interface_id, biomolecule_id, *expr, **kwargs):
        """
        Returns a list of `Contact` objects that exist in the pairwise interaction
        between two chain in an `Interface`.

        Parameters
        ----------
        interface_id : int
            `Interface` identifier.
        biomolecule_id : int

        *expr : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried Entities
        ----------------
        Contact, AtomBgn (Atom), AtomEnd (Atom), PeptideBgn (Peptide),
        PeptideEnd (Peptide), Interface

        Returns
        -------
        contacts : list
            List of `contact` objects.

         Examples
        --------
        >>> ContactAdaptor().fetch_all_by_interface_id(1)
        <Contact()>
        """
        AtomBgn = aliased(Atom)
        AtomEnd = aliased(Atom)
        PeptideBgn = aliased(Residue)
        PeptideEnd = aliased(Residue)

        query = self.query.join((AtomBgn, and_(AtomBgn.atom_id==Contact.atom_bgn_id,
                                               AtomBgn.biomolecule_id==Contact.biomolecule_id)),
                                (AtomEnd, and_(AtomEnd.atom_id==Contact.atom_end_id,
                                               AtomEnd.biomolecule_id==Contact.biomolecule_id)))
        query = query.join((PeptideBgn, PeptideBgn.residue_id==AtomBgn.residue_id),
                           (PeptideEnd, PeptideEnd.residue_id==AtomEnd.residue_id))
        query = query.join(Interface, and_(Interface.chain_bgn_id==PeptideBgn.chain_id,
                                           Interface.chain_end_id==PeptideEnd.chain_id))

        query = query.filter(and_(Interface.interface_id==interface_id,
                                  Contact.biomolecule_id==biomolecule_id, *expr))

        return query

    @paginate
    def fetch_all_by_groove_id(self, groove_id, biomolecule_id, *expr, **kwargs):
        """
        Returns all the contacts between the peptides and nucleotides in this groove.
        This method will NOT return interactions for any non-peptide and non-nucleotide
        residues, (e.g. water).

        Parameters
        ----------
        groove_id : int
            Primary key of the groove.
        *expr : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried Entities
        ----------------
        Contact, AtomBgn (Atom), AtomEnd (Atom), Peptide, Nucleotide, Groove

        Returns
        -------
        contacts : list
            all the contacts in this groove.

         Examples
        --------
        >>>
        """
        AtomBgn = aliased(Atom)
        AtomEnd = aliased(Atom)

        where = and_(Groove.groove_id==groove_id,
                     Contact.biomolecule_id==biomolecule_id,
                     *expr)

        query = self.query.join(
            (AtomBgn, and_(AtomBgn.atom_id==Contact.atom_bgn_id,
                           AtomBgn.biomolecule_id==Contact.biomolecule_id)),
            (AtomEnd, and_(AtomEnd.atom_id==Contact.atom_end_id,
                           AtomEnd.biomolecule_id==Contact.biomolecule_id)))

        bgn = query.join(
            (Peptide, Peptide.residue_id==AtomBgn.residue_id),
            (Nucleotide, Nucleotide.residue_id==AtomEnd.residue_id),
            (Groove, and_(Groove.chain_prot_id==Peptide.chain_id,
                          Groove.chain_nuc_id==Nucleotide.chain_id))).filter(where)

        end = query.join(
            (Peptide, Peptide.residue_id==AtomEnd.residue_id),
            (Nucleotide, Nucleotide.residue_id==AtomBgn.residue_id),
            (Groove, and_(Groove.chain_prot_id==Peptide.chain_id,
                          Groove.chain_nuc_id==Nucleotide.chain_id))).filter(where)

        query = bgn.union_all(end)

        return query

    @paginate
    def fetch_all_by_ligand_fragment_id(self, ligand_fragment_id, biomolecule_id,
                                        *expr, **kwargs):
        """
        """
        where = and_(LigandFragmentAtom.ligand_fragment_id==ligand_fragment_id,
                     Contact.biomolecule_id==biomolecule_id, *expr)

        bgn = self.query.join(LigandFragmentAtom, LigandFragmentAtom.atom_id==Contact.atom_bgn_id)
        bgn = bgn.filter(where)

        end = self.query.join(LigandFragmentAtom, LigandFragmentAtom.atom_id==Contact.atom_end_id)
        end = end.filter(where)

        # eager-load the interacting atoms
        if kwargs.get('load_atoms'):
            bgn = bgn.options(joinedload(Contact.AtomBgn, innerjoin=True),
                              joinedload(Contact.AtomEnd, innerjoin=True))
            end = end.options(joinedload(Contact.AtomBgn, innerjoin=True),
                              joinedload(Contact.AtomEnd, innerjoin=True))

        query = bgn.union_all(end)

        return query

    @paginate
    def fetch_all_by_ligand_id_and_atom_names(self, ligand_id, biomolecule_id,
                                              atom_names, *expr, **kwargs):
        """
        Returns all contacts that are part of the ligand with the given ligand identifier
        and match the specified list of atom names.

        Parameters
        ----------
        ligand__id : int
            `Ligand` identifier.
        biomolecule_id : int

        *expr : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried Entities
        -----
        Contact, Atom, Hetatm

        Returns
        -------
        contacts : list
            List of `Contact` objects.
        """
        where = and_(Hetatm.ligand_id==ligand_id,
                     Atom.biomolecule_id==biomolecule_id,
                     Contact.biomolecule_id==biomolecule_id,
                     Atom.atom_name==func.any(atom_names), *expr)

        bgn = self.query.join(Atom, Atom.atom_id==Contact.atom_bgn_id)
        bgn = bgn.join(Hetatm, Hetatm.atom_id==Atom.atom_id)
        bgn = bgn.filter(where)

        end = self.query.join(Atom, Atom.atom_id==Contact.atom_end_id)
        end = end.join(Hetatm, Hetatm.atom_id==Atom.atom_id)
        end = end.filter(where)

        return bgn.union_all(end)

from ..models.hetatm import Hetatm
from ..models.ligandcomponent import LigandComponent
from ..models.ligand import Ligand
from ..models.ligandfragmentatom import LigandFragmentAtom
from ..models.contact import Contact
from ..models.atom import Atom
from ..models.peptide import Peptide
from ..models.nucleotide import Nucleotide
from ..models.residue import Residue
from ..models.interface import Interface
from ..models.groove import Groove