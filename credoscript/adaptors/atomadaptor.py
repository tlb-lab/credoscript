from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import and_

from credoscript import Session, binding_sites, interface_residues
from credoscript.mixins.base import paginate

class AtomAdaptor(object):
    """
    """
    def __init__(self, paginate=False, per_page=100):
        self.query = Atom.query
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
        Returns a list of `Atoms` that are part of the ligand with the given identifier.

        Parameters
        ----------
        ligand_id : int
            `Ligand` identifier.
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
    def fetch_all_in_contact_with_ligand_id(self, ligand_id, biomolecule_id,
                                            *expr, **kwargs):
        """
        Returns all atoms that are in contact with the ligand having the specified
        ligand identifier.

        Parameters
        ----------
        ligand_id : int
            `Ligand` identifier.
        *expr : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Joins
        -----
        Atom, credo.tables['credo.binding_sites']

        Returns
        -------
        atoms : list
            List of `Atom` objects.
        """
        query = self.query.join(binding_sites, binding_sites.c.residue_id==Atom.residue_id)
        query = query.filter(and_(binding_sites.c.ligand_id==ligand_id,
                                  Atom.biomolecule_id==biomolecule_id,
                                  *expr))

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
        Atom, Contact, ligand_fragment_atoms

        Returns
        -------
        atoms : list
            List of `Atom` objects.
        """
        where = and_(Atom.biomolecule_id==biomolecule_id,
                     LigandFragmentAtom.ligand_fragment_id==ligand_fragment_id,
                     *expr)

        bgn = self.query.join('ContactsBgn')
        bgn = bgn.join(LigandFragmentAtom, LigandFragmentAtom.atom_id==Contact.atom_end_id)
        bgn = bgn.filter(where)

        end = self.query.join('ContactsEnd')
        end = end.join(LigandFragmentAtom, LigandFragmentAtom.atom_id==Contact.atom_bgn_id)
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

    @paginate
    def fetch_all_water_in_contact_with_residue_id(self, residue_id, biomolecule_id,
                                                   *expr, **kwargs):
        """
        """
        where = and_(Atom.residue_id==residue_id,
                     Atom.biomolecule_id==Contact.biomolecule_id,
                     Contact.biomolecule_id==biomolecule_id)

        bgn = Contact.query.join('AtomBgn').filter(where)
        bgn = bgn.with_entities(Contact.biomolecule_id.label('biomolecule_id'),
                                Contact.atom_end_id.label('atom_other_id'))
        bgn = bgn.filter(Contact.structural_interaction_type_bm.op('&')(1) == 1)

        end = Contact.query.join('AtomEnd').filter(where)
        end = end.with_entities(Contact.biomolecule_id.label('biomolecule_id'),
                                Contact.atom_bgn_id.label('atom_other_id'))
        end = end.filter(Contact.structural_interaction_type_bm.op('&')(64) == 64)

        sq = bgn.union(end).subquery()

        query = self.query.join(sq, and_(sq.c.atom_other_id==Atom.atom_id,
                                         sq.c.biomolecule_id==Atom.biomolecule_id))
        query = query.filter(and_(*expr))

        return query

    @paginate
    def fetch_all_water_in_contact_with_ligand_id(self, ligand_id, biomolecule_id,
                                                  *expr, **kwargs):
        """
        """
        session = Session()

        whereclause = and_(Hetatm.ligand_id==ligand_id, Contact.is_hbond==True,
                           Contact.is_any_wat,
                           Contact.biomolecule_id==biomolecule_id,
                           *expr)

        bgn = session.query(Contact.atom_bgn_id.label('atom_id'))
        bgn = bgn.join(Hetatm, Hetatm.atom_id==Contact.atom_end_id)
        bgn = bgn.filter(whereclause)

        end = session.query(Contact.atom_end_id.label('atom_id'))
        end = end.join(Hetatm, Hetatm.atom_id==Contact.atom_bgn_id)
        end = end.filter(whereclause)

        subquery = bgn.union(end).subquery()

        query = self.query.join(subquery, subquery.c.atom_id==Atom.atom_id)

        return query

    @paginate
    def fetch_all_water_in_contact_with_interface_id(self, interface_id, biomolecule_id,
                                                     *expr, **kwargs):
        """
        Returns the water atoms that form interactions with both chains in the
        `Interface`.

        SELECT a.*
            FROM credo.atoms a
            JOIN credo.contacts cs
                 ON cs.atom_bgn_id = a.atom_id
                 AND a.biomolecule_id = cs.biomolecule_id
            JOIN credo.atoms ia
                 ON ia.atom_id = cs.atom_end_id
                 AND ia.biomolecule_id = cs.biomolecule_id
            JOIN credo.interface_residues ir
                 ON ir.residue_end_id = ia.residue_id
           WHERE a.biomolecule_id = 11
                 AND ir.interface_id = 1
                 AND cs.structural_interaction_type_bm & 64 = 64
           UNION
           SELECT DISTINCT a.*
            FROM credo.atoms a
            JOIN credo.contacts cs
                 ON cs.atom_end_id = a.atom_id
                 AND a.biomolecule_id = cs.biomolecule_id
            JOIN credo.atoms ia
                 ON ia.atom_id = cs.atom_bgn_id
                 AND ia.biomolecule_id = cs.biomolecule_id
            JOIN credo.interface_residues ir
                 ON ir.residue_bgn_id = ia.residue_id
           WHERE a.biomolecule_id = 11
                 AND ir.interface_id = 1
                 AND cs.structural_interaction_type_bm & 1 = 1
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
from ..models.interface import Interface
from ..models.chain import Chain
from ..models.ligandfragmentatom import LigandFragmentAtom