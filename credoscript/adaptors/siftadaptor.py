from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import and_, cast, func
from sqlalchemy.dialects.postgresql import INTEGER

from credoscript import Session, binding_sites

class SIFtAdaptor(object):
    """
    This adaptors is used to fetch Structural Interaction Fingerprints (SIFt) in
    the form [(Residue, sum of interactions),...] for various CREDO entities.
    """
    def _fetch_sift(self, session, subquery):
        """
        """
        # residue id and sum of structural interaction fingerprints
        fields = (subquery.c.residue_id,
                  func.sum(cast(subquery.c.credo_contacts_is_clash, INTEGER)).label('is_clash'),
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

        # aggregate to get the sum
        sift = session.query(*fields).group_by('residue_id').order_by('residue_id').subquery()

        # include the residue object in result set
        query = session.query(Residue, sift.c.is_clash, sift.c.is_covalent,
                              sift.c.is_vdw_clash, sift.c.is_vdw, sift.c.is_proximal,
                              sift.c.is_hbond, sift.c.is_weak_hbond, sift.c.is_xbond,
                              sift.c.is_ionic, sift.c.is_metal_complex,
                              sift.c.is_aromatic, sift.c.is_hydrophobic,
                              sift.c.is_carbonyl)

        query = query.join(sift, sift.c.residue_id==Residue.residue_id)

        return query.all()

    def fetch_by_residue_id(self, residue_id, biomolecule_id, *expr):
        """
        """
        session = Session()

        where = and_(Atom.residue_id==residue_id,
                     Contact.biomolecule_id==biomolecule_id,
                     Contact.is_same_entity==False,
                     *expr)

        bgn = session.query(Contact).join('AtomBgn').filter(where)
        end = session.query(Contact).join('AtomEnd').filter(where)

        subquery = bgn.union(end).subquery(name='contacts')

        sift = (func.sum(cast(subquery.c.credo_contacts_is_clash, INTEGER)),
                func.sum(cast(subquery.c.credo_contacts_is_covalent, INTEGER)),
                func.sum(cast(subquery.c.credo_contacts_is_vdw_clash, INTEGER)),
                func.sum(cast(subquery.c.credo_contacts_is_vdw, INTEGER)),
                func.sum(cast(subquery.c.credo_contacts_is_proximal, INTEGER)),
                func.sum(cast(subquery.c.credo_contacts_is_hbond, INTEGER)),
                func.sum(cast(subquery.c.credo_contacts_is_weak_hbond, INTEGER)),
                func.sum(cast(subquery.c.credo_contacts_is_xbond, INTEGER)),
                func.sum(cast(subquery.c.credo_contacts_is_ionic, INTEGER)),
                func.sum(cast(subquery.c.credo_contacts_is_metal_complex, INTEGER)),
                func.sum(cast(subquery.c.credo_contacts_is_aromatic, INTEGER)),
                func.sum(cast(subquery.c.credo_contacts_is_hydrophobic, INTEGER)),
                func.sum(cast(subquery.c.credo_contacts_is_carbonyl, INTEGER)))

        return session.query(*sift).first()

    def fetch_by_own_chain_id(self, chain_id, biomolecule_id, *expr, **kwargs):
        """
        Returns the SIFt of all OTHER entities with residues that are part of THIS
        chain.
        """
        session = Session()

        query = session.query(Atom.residue_id.label('residue_id'), Contact)
        query = query.select_from(Contact)

        where = and_(Residue.chain_id==chain_id,
                     Contact.biomolecule_id==biomolecule_id,
                     Contact.is_same_entity==False, Contact.is_secondary==False,
                     *expr)

        bgn = query.join('AtomBgn','Residue').filter(where)
        end = query.join('AtomBgn','Residue').filter(where)

        subquery = bgn.union(end).subquery()

        return self._fetch_sift(session, subquery)

    def fetch_by_ligand_id(self, ligand_id, biomolecule_id, *expr, **kwargs):
        """
        Returns the SIFt of a ligand.
        """
        session = Session()

        where = and_(binding_sites.c.ligand_id==ligand_id,
                     Contact.biomolecule_id==biomolecule_id,
                     Contact.is_same_entity==False,
                     *expr)

        query = session.query(Atom.residue_id.label('residue_id'), Contact)
        query = query.select_from(Contact)

        bgn = query.join('AtomBgn')
        bgn = bgn.join(binding_sites, binding_sites.c.residue_id==Atom.residue_id)
        bgn = bgn.filter(where)

        end = query.join('AtomEnd')
        end = end.join(binding_sites, binding_sites.c.residue_id==Atom.residue_id)
        end = end.filter(where)

        subquery = bgn.union_all(end).subquery()

        return self._fetch_sift(session, subquery)

    def fetch_by_ligand_id_and_atom_names(self, ligand_id, biomolecule_id,
                                          atom_names, *expr, **kwargs):
        """
        Returns the SIFt of a part of a ligand (defined by the input atom names).

        Queried Entities
        ----------------
        Contact, Atom, MatchAtom (Atom), Hetatm
        """
        session = Session()
        MatchAtom = aliased(Atom)

        where = and_(MatchAtom.atom_name==func.any(atom_names),
                     Contact.biomolecule_id==biomolecule_id,
                     Contact.is_same_entity==False,
                     Hetatm.ligand_id==ligand_id, *expr)

        query = session.query(Atom.residue_id.label('residue_id'), Contact)
        query = query.select_from(Contact)

        bgn = query.join('AtomBgn')
        bgn = bgn.join(MatchAtom, and_(MatchAtom.atom_id==Contact.atom_end_id,
                                       MatchAtom.biomolecule_id==Contact.biomolecule_id))
        bgn = bgn.join(Hetatm, Hetatm.atom_id==MatchAtom.atom_id)
        bgn = bgn.filter(where)

        end = query.join('AtomEnd')
        end = end.join(MatchAtom, and_(MatchAtom.atom_id==Contact.atom_bgn_id,
                                       MatchAtom.biomolecule_id==Contact.biomolecule_id))
        end = end.join(Hetatm, Hetatm.atom_id==MatchAtom.atom_id)
        end = end.filter(where)

        subquery = bgn.union_all(end).subquery()

        return self._fetch_sift(session, subquery)

    def fetch_by_ligand_fragment_id(self, ligand_fragment_id, biomolecule_id, *expr):
        """
        """
        session = Session()

        where = and_(LigandFragmentAtom.ligand_fragment_id==ligand_fragment_id,
                     Contact.biomolecule_id==biomolecule_id,
                     Contact.is_same_entity==False,
                     *expr)

        query = session.query(Atom.residue_id.label('residue_id'), Contact)
        query = query.select_from(Contact)

        bgn = query.join(Atom, and_(Atom.atom_id==Contact.atom_bgn_id,
                                    Atom.biomolecule_id==Contact.biomolecule_id))
        bgn = bgn.join(LigandFragmentAtom, LigandFragmentAtom.atom_id==Contact.atom_end_id)
        bgn = bgn.filter(where)

        end = query.join(Atom, and_(Atom.atom_id==Contact.atom_end_id,
                                    Atom.biomolecule_id==Contact.biomolecule_id))
        end = end.join(LigandFragmentAtom, LigandFragmentAtom.atom_id==Contact.atom_bgn_id)
        end = end.filter(where)

        subquery = bgn.union(end).subquery()

        return self._fetch_sift(session, subquery)

from ..models.contact import Contact
from ..models.atom import Atom
from ..models.hetatm import Hetatm
from ..models.residue import Residue
from ..models.ligandfragmentatom import LigandFragmentAtom