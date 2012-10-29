from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import and_, func

from credoscript import interface_residues
from credoscript.mixins.base import paginate

class AtomAdaptor(object):
    """
    Class to fetch atoms from CREDO.
    """
    def __init__(self, dynamic=False, paginate=False, per_page=100):
        self.query = Atom.query
        self.dynamic = dynamic
        self.paginate = paginate
        self.per_page = per_page

    def fetch_by_atom_id(self, atom_id, biomolecule_id):
        """
        Parameters
        ----------
        atom_id : int
            Primary key of the `Contact` in CREDO.
        biomolecule_id : int

        Returns
        -------
        Atom
            CREDO `Atom` object having this atom_id as primary key.

        Examples
        --------
        >>> AtomAdaptor().fetch_by_atom_id(1)
        <Atom(1)>
        """
        query = self.query.filter_by(atom_id=atom_id, biomolecule_id=biomolecule_id)

        return query.first()

    @paginate
    def fetch_all_by_ligand_id(self, ligand_id, biomolecule_id, *expr, **kwargs):
        """
        Returns a list of `Atoms` that are part of the ligand with the given
        identifier.

        Parameters
        ----------
        ligand_id : int
            `Ligand` identifier.
        biomolecule_id : int
            `Biomolecule` identifier.
        *expr : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Joins
        -----
        Atom, Hetatm

        Returns
        -------
        contacts : list
            List of `Atom` objects.

         Examples
        --------
        >>> AtomAdaptor().fetch_all_by_ligand_id(4343)
        [<Atom(C01  )>, <Atom(C02  )>, <Atom(N03  )>, <Atom(C04  )>, <Atom(O05  )>,...]

        """
        query = self.query.join((Hetatm, Hetatm.atom_id==Atom.atom_id))
        query = query.filter(and_(Hetatm.ligand_id==ligand_id,
                                  Atom.biomolecule_id==biomolecule_id, *expr))

        return query

    @paginate
    def fetch_all_by_chain_id(self, chain_id, biomolecule_id, *expr, **kwargs):
        """
        """
        query = self.query.join('Residue')
        query = query.filter(and_(Residue.chain_id==chain_id,
                                  Atom.biomolecule_id==biomolecule_id, *expr))

        return query

    @paginate
    def fetch_all_by_aromatic_ring_id(self, aromatic_ring_id, biomolecule_id,
                                      *expr, **kwargs):
        """
        """
        query = self.query.join(AromaticRingAtom, AromaticRingAtom.atom_id==Atom.atom_id)
        query = query.filter(and_(AromaticRingAtom.aromatic_ring_id==aromatic_ring_id,
                                  Atom.biomolecule_id==biomolecule_id, *expr))

        return query

    @paginate
    def fetch_all_by_ligand_id_and_atom_names(self, ligand_id, biomolecule_id,
                                              atom_names, *expr, **kwargs):
        """
        Returns all atoms that are part of the ligand with the given ligand identifier
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
        Atom, Hetatm

        Returns
        -------
        atoms : list
            List of `Atom` objects.
        """
        query = self.query.join(Hetatm, Hetatm.atom_id==Atom.atom_id)
        query = query.filter(and_(Hetatm.ligand_id==ligand_id,
                                  Atom.biomolecule_id==biomolecule_id,
                                  Atom.atom_name==func.any(atom_names),
                                  *expr))

        return query

    @paginate
    def fetch_all_in_contact_with_residue_id(self, residue_id, biomolecule_id,
                                             *expr, **kwargs):
        """
        Returns all atoms that are in contact with the residue having the specified
        residue identifier.

        Parameters
        ----------
        residue : int
            `residue` identifier.
        biomolecule_id : int
            `Biomolecule` identifier.
        *expr : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Joins
        -----
        Atom, Contact, ResAtom (Atom)

        Returns
        -------
        atoms : list
            List of `Atom` objects.
        """
        ResAtom = aliased(Atom)

        where = and_(ResAtom.residue_id==residue_id,
                     ResAtom.biomolecule_id==biomolecule_id,
                     Contact.biomolecule_id==biomolecule_id, *expr)

        bgn = self.query.join('ContactsBgn')
        bgn = bgn.join(ResAtom, ResAtom.atom_id==Contact.atom_end_id)
        bgn = bgn.filter(where)

        end = self.query.join('ContactsEnd')
        end = end.join(ResAtom, ResAtom.atom_id==Contact.atom_bgn_id)
        end = end.filter(where)

        query = bgn.union(end)

        return query

    @paginate
    def fetch_all_in_contact_with_ligand_id(self, ligand_id, biomolecule_id,
                                            *expr, **kwargs):
        """
        Returns all atoms that are in contact with the ligand having the specified
        ligand identifier.

        Parameters
        ----------
        ligand_id : int
            `Ligand` identifier.
        biomolecule_id : int
            `Biomolecule` identifier.
        *expr : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Joins
        -----
        Atom, Contact, Hetatm

        Returns
        -------
        atoms : list
            List of `Atom` objects.
        """
        where = and_(Hetatm.ligand_id==ligand_id,
                     Contact.biomolecule_id==biomolecule_id, *expr)

        bgn = self.query.join('ContactsBgn')
        bgn = bgn.join(Hetatm, Hetatm.atom_id==Contact.atom_end_id)
        bgn = bgn.filter(where)

        end = self.query.join('ContactsEnd')
        end = end.join(Hetatm, Hetatm.atom_id==Contact.atom_bgn_id)
        end = end.filter(where)

        query = bgn.union(end)

        return query

    @paginate
    def fetch_all_in_contact_with_ligand_fragment_id(self, ligand_fragment_id,
                                                     biomolecule_id, *expr, **kwargs):
        """
        Returns all atoms that are in contact with the ligand fragment having the specified
        identifier.

        Parameters
        ----------
        ligand_fragment_id : int
            `LigandFragment` identifier.
        biomolecule_id : int

        *expr : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Joins
        -----
        Atom, Contact, LigandFragmentAtom

        Returns
        -------
        atoms : list
            List of `Atom` objects.
        """
        where = and_(Atom.biomolecule_id==biomolecule_id,
                     LigandFragmentAtom.ligand_fragment_id==ligand_fragment_id,
                     *expr)

        bgn = self.query.join('ContactsBgn')
        bgn = bgn.join(LigandFragmentAtom,
                       LigandFragmentAtom.atom_id==Contact.atom_end_id)
        bgn = bgn.filter(where)

        end = self.query.join('ContactsEnd')
        end = end.join(LigandFragmentAtom,
                       LigandFragmentAtom.atom_id==Contact.atom_bgn_id)
        end = end.filter(where)

        query = bgn.union(end)

        return query

    @paginate
    def fetch_all_water_in_contact_with_atom_id(self, atom_id, biomolecule_id,
                                                *expr, **kwargs):
        """
        """
        bgn = self.query.join('ContactsBgn')
        bgn = bgn.filter(Contact.structural_interaction_type_bm.op('&')(1) == 1)
        bgn = bgn.filter(and_(Contact.biomolecule_id==biomolecule_id, *expr))

        end = self.query.join('ContactsEnd')
        end = end.filter(Contact.structural_interaction_type_bm.op('&')(64) == 64)
        end = end.filter(and_(Contact.biomolecule_id==biomolecule_id, *expr))

        query = bgn.union(end)

        return query

    def fetch_all_water_in_contact_with_residue_id(self, residue_id, biomolecule_id,
                                                   *expr, **kwargs):
        """
        """
        return self.fetch_all_in_contact_with_residue_id(residue_id, biomolecule_id,
                                                         Contact.is_any_wat,
                                                         *expr, **kwargs)

    def fetch_all_water_in_contact_with_ligand_id(self, ligand_id, biomolecule_id,
                                                  *expr, **kwargs):
        """
        """
        return self.fetch_all_in_contact_with_ligand_id(ligand_id, biomolecule_id,
                                                        Contact.is_any_wat,
                                                        *expr, **kwargs)

    @paginate
    def fetch_all_water_in_contact_with_interface_id(self, interface_id, biomolecule_id,
                                                     *expr, **kwargs):
        """
        Returns the water atoms that form interactions with both chains in the
        `Interface`.
        """
        IAtom = aliased(Atom)

        bgn = self.query.join('ContactsBgn')
        bgn = bgn.join(IAtom, and_(IAtom.atom_id==Contact.atom_end_id,
                                   IAtom.biomolecule_id==Contact.biomolecule_id))
        bgn = bgn.join(interface_residues,
                       interface_residues.c.residue_end_id==IAtom.residue_id)
        bgn = bgn.filter(and_(Atom.biomolecule_id==biomolecule_id,
                              interface_residues.c.interface_id==interface_id,
                              Contact.structural_interaction_type_bm.op('&')(64) == 64,
                              *expr))

        end = self.query.join('ContactsEnd')
        end = end.join(IAtom, and_(IAtom.atom_id==Contact.atom_bgn_id,
                                   IAtom.biomolecule_id==Contact.biomolecule_id))
        end = end.join(interface_residues,
                       interface_residues.c.residue_bgn_id==IAtom.residue_id)
        end = end.filter(and_(Atom.biomolecule_id==biomolecule_id,
                              interface_residues.c.interface_id==interface_id,
                              Contact.structural_interaction_type_bm.op('&')(1) == 1,
                              *expr))

        return bgn.union(end)

from ..models.contact import Contact
from ..models.aromaticringatom import AromaticRingAtom
from ..models.atom import Atom
from ..models.hetatm import Hetatm
from ..models.residue import Residue
from ..models.ligandfragmentatom import LigandFragmentAtom
