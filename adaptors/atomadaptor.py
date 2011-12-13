from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import and_

from credoscript import session, binding_sites

class AtomAdaptor(object):
    '''
    '''
    def __init__(self):
        '''
        '''
        self.query = session.query(Atom)

    def fetch_by_atom_id(self, atom_id):
        '''
        Parameters
        ----------
        atom_id : int
            Primary key of the `Contact` in CREDO.

        Returns
        -------
        Atom
            CREDO `Atom` object having this atom_id as primary key.

        Examples
        --------
        >>> AtomAdaptor().fetch_by_atom_id(1)
        <Atom(1)>
        '''
        return self.query.get(atom_id)

    def fetch_all_by_ligand_id(self, ligand_id, *expressions):
        '''
        Returns a list of `Atoms` that are part of the ligand with the given identifier.

        Parameters
        ----------
        ligand_id : int
            `Ligand` identifier.
        *expressions : BinaryExpressions, optional
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

        '''
        query = self.query.join(
            (Hetatm, Hetatm.atom_id==Atom.atom_id)
            ).filter(and_(Hetatm.ligand_id==ligand_id, *expressions))

        return query.all()

    def fetch_all_by_chain_id(self, chain_id, *expressions):
        '''
        '''
        query = self.query.join('Residue').filter(and_(Residue.chain_id==chain_id,
                                                       Residue.biomolecule_id==Atom.biomolecule_id, # PARTITION CONSTRAINT-EXCLUSION
                                                       *expressions))

        return query.all()

    def fetch_all_water_by_atom_id(self, atom_id, *expressions):
        '''
        '''
        whereclause = and_(Contact.atom_bgn_id==atom_id, Contact.is_hbond==True)
        
        bgn = session.query(Contact.atom_end_id.label('atom_other_id')).filter(whereclause)
        end = session.query(Contact.atom_bgn_id.label('atom_other_id')).filter(whereclause)

        subquery = bgn.union_all(end).subquery()

        query = self.query.join(
            (subquery, subquery.c.atom_other_id==Atom.atom_id),
            (Residue, and_(Residue.residue_id==Atom.residue_id,
                           Residue.biomolecule_id==Atom.biomolecule_id)))

        return query.filter(and_(Residue.res_name=='HOH', *expressions)).all()

    def fetch_all_water_by_residue_id(self, residue_id, *expressions):
        '''
        '''
        u1 = session.query(Contact.atom_end_id.label('atom_other_id')).join(
            (Atom, Atom.atom_id==Contact.atom_bgn_id)
            ).filter(and_(Atom.residue_id==residue_id, Contact.is_hbond==True))

        u2 = session.query(Contact.atom_bgn_id.label('atom_other_id')).join(
            (Atom, Atom.atom_id==Contact.atom_end_id)
            ).filter(and_(Atom.residue_id==residue_id, Contact.is_hbond==True))

        sq = u1.union(u2).subquery()

        query = self.query.join(
            (sq, sq.c.atom_other_id==Atom.atom_id),
            (Residue, Residue.residue_id==Atom.residue_id))

        return query.filter(and_(Residue.res_name=='HOH', *expressions)).all()

    def fetch_all_water_by_ligand_id(self, ligand_id, *expressions):
        '''
        '''
        u1 = session.query(Contact.atom_end_id.label('atom_other_id')).join(
            (Hetatm, Hetatm.atom_id==Contact.atom_bgn_id)
            ).filter(and_(Hetatm.ligand_id==ligand_id, Contact.is_hbond==True))

        u2 = session.query(Contact.atom_bgn_id.label('atom_other_id')).join(
            (Hetatm, Hetatm.atom_id==Contact.atom_end_id)
            ).filter(and_(Hetatm.ligand_id==ligand_id, Contact.is_hbond==True))

        sq = u1.union(u2).subquery()

        query = self.query.join(
            (sq, sq.c.atom_other_id==Atom.atom_id),
            (Residue, Residue.residue_id==Atom.residue_id))

        return query.filter(and_(Residue.res_name=='HOH', *expressions)).all()

    def fetch_all_water_by_interface_id(self, interface_id, *expressions):
        '''
        Returns the water atoms that form interactions with both chains in the
        `Interface`.
        '''
        Water = aliased(Atom)
        WaterRes = aliased(Residue)

        i_bgn_bgn = session.query(Water).join(
            (WaterRes, WaterRes.residue_id==Water.residue_id),
            (Contact, Contact.atom_end_id==Water.atom_id),
            (Atom, Atom.atom_id==Contact.atom_bgn_id),
            (Residue, Residue.residue_id==Atom.residue_id),
            (Interface, Interface.chain_bgn_id==Residue.chain_id)
            ).filter(and_(WaterRes.res_name=='HOH',
                          Interface.interface_id==interface_id,
                          Contact.is_hbond==True))

        i_bgn_end = session.query(Water).join(
            (WaterRes, WaterRes.residue_id==Water.residue_id),
            (Contact, Contact.atom_bgn_id==Water.atom_id),
            (Atom, Atom.atom_id==Contact.atom_end_id),
            (Residue, Residue.residue_id==Atom.residue_id),
            (Interface, Interface.chain_bgn_id==Residue.chain_id)
            ).filter(and_(WaterRes.res_name=='HOH',
                          Interface.interface_id==interface_id,
                          Contact.is_hbond==True))

        sq_bgn = i_bgn_bgn.union(i_bgn_end)

        i_end_bgn = session.query(Water).join(
            (WaterRes, WaterRes.residue_id==Water.residue_id),
            (Contact, Contact.atom_end_id==Water.atom_id),
            (Atom, Atom.atom_id==Contact.atom_bgn_id),
            (Residue, Residue.residue_id==Atom.residue_id),
            (Interface, Interface.chain_end_id==Residue.chain_id)
            ).filter(and_(WaterRes.res_name=='HOH',
                          Interface.interface_id==interface_id,
                          Contact.is_hbond==True))

        i_end_end = session.query(Water).join(
            (WaterRes, WaterRes.residue_id==Water.residue_id),
            (Contact, Contact.atom_bgn_id==Water.atom_id),
            (Atom, Atom.atom_id==Contact.atom_end_id),
            (Residue, Residue.residue_id==Atom.residue_id),
            (Interface, Interface.chain_end_id==Residue.chain_id)
            ).filter(and_(WaterRes.res_name=='HOH',
                          Interface.interface_id==interface_id,
                          Contact.is_hbond==True))

        sq_end = i_end_bgn.union(i_end_end)

        return sq_bgn.intersect(sq_end).all()

    def fetch_all_in_contact_with_ligand_id(self, ligand_id, *expressions):
        '''
        Returns all atoms that are in contact with the ligand having the specified
        ligand identifier.

        Parameters
        ----------
        ligand_id : int
            `Ligand` identifier.
        *expressions : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Joins
        -----
        Atom, credo.tables['credo.binding_sites']

        Returns
        -------
        atoms : list
            List of `Atom` objects.
        '''
        return self.query.join(
            (binding_sites, binding_sites.c.residue_id==Atom.residue_id)
            ).filter(and_(binding_sites.c.ligand_id==ligand_id, *expressions)).all()

    def fetch_all_in_contact_with_ligand_fragment_id(self, ligand_fragment_id, *expressions):
        '''
        Returns all atoms that are in contact with the ligand fragment having the specified
        identifier.

        Parameters
        ----------
        ligand_fragment_id : int
            `LigandFragment` identifier.
        *expressions : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Joins
        -----
        Atom, Contact, ligand_fragment_atoms

        Returns
        -------
        atoms : list
            List of `Atom` objects.
        '''
        bgn = self.query.join(
            (Contact, Contact.atom_bgn_id==Atom.atom_id),
            (ligand_fragment_atoms, LigandFragmentAtom.atom_id==Contact.atom_end_id)
            ).filter(and_(LigandFragmentAtom.ligand_fragment_id==ligand_fragment_id, *expressions))

        end = self.query.join(
            (Contact, Contact.atom_end_id==Atom.atom_id),
            (ligand_fragment_atoms, LigandFragmentAtom.atom_id==Contact.atom_bgn_id)
            ).filter(and_(LigandFragmentAtom.ligand_fragment_id==ligand_fragment_id, *expressions))

        return bgn.union(end).all()

from ..models.contact import Contact
from ..models.atom import Atom
from ..models.hetatm import Hetatm
from ..models.residue import Residue
from ..models.interface import Interface
from ..models.chain import Chain
from ..models.ligandfragmentatom import LigandFragmentAtom