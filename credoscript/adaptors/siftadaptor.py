from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import and_, cast, func
from sqlalchemy.dialects.postgresql import INTEGER

class SIFtAdaptor(object):
    """
    This adaptors is used to fetch Structural Interaction Fingerprints (SIFt) in
    the form [(Residue, sum of interactions),...] for various CREDO entities.
    """
    @property
    def _sift(self):
        sift = (func.sum(cast(Contact.is_clash, INTEGER)).label('is_clash'),
                func.sum(cast(Contact.is_covalent, INTEGER)).label('is_covalent'),
                func.sum(cast(Contact.is_vdw_clash, INTEGER)).label('is_vdw_clash'),
                func.sum(cast(Contact.is_vdw, INTEGER)).label('is_vdw'),
                func.sum(cast(Contact.is_proximal, INTEGER)).label('is_proximal'),
                func.sum(cast(Contact.is_hbond, INTEGER)).label('is_hbond'),
                func.sum(cast(Contact.is_weak_hbond, INTEGER)).label('is_weak_hbond'),
                func.sum(cast(Contact.is_xbond, INTEGER)).label('is_xbond'),
                func.sum(cast(Contact.is_ionic, INTEGER)).label('is_ionic'),
                func.sum(cast(Contact.is_metal_complex, INTEGER)).label('is_metal_complex'),
                func.sum(cast(Contact.is_aromatic, INTEGER)).label('is_aromatic'),
                func.sum(cast(Contact.is_hydrophobic, INTEGER)).label('is_hydrophobic'),
                func.sum(cast(Contact.is_carbonyl, INTEGER)).label('is_carbonyl'))

        return sift

    def _fetch_sift(self, subquery):
        """
        """
        query = Residue.query.join(subquery, subquery.c.residue_id==Residue.residue_id)
        query = query.add_columns(subquery.c.is_clash, subquery.c.is_covalent,
                                  subquery.c.is_vdw_clash, subquery.c.is_vdw,
                                  subquery.c.is_proximal, subquery.c.is_hbond,
                                  subquery.c.is_weak_hbond, subquery.c.is_xbond,
                                  subquery.c.is_ionic, subquery.c.is_metal_complex,
                                  subquery.c.is_aromatic, subquery.c.is_hydrophobic,
                                  subquery.c.is_carbonyl)

        return query.all()

    def fetch_by_own_residue_id(self, residue_id, biomolecule_id, *expr):
        """
        """
        where = and_(Atom.residue_id==residue_id,
                     Contact.biomolecule_id==biomolecule_id,
                     Contact.is_same_entity==False,
                     *expr)

        query = Contact.query.join('Atoms').filter(where)

        return query.with_entities(*self._sift).first()

    def fetch_by_own_chain_id(self, chain_id, biomolecule_id, *expr, **kwargs):
        """
        Returns the SIFt of all OTHER entities with residues that are part of THIS
        chain.
        """
        where = and_(Residue.chain_id==chain_id,
                     Contact.biomolecule_id==biomolecule_id,
                     Contact.is_same_entity==False,
                     *expr)

        query = Residue.query.join('Atoms','Contacts').filter(where)
        query = query.add_columns(*self._sift)
        query = query.group_by(Residue).order_by(Residue.residue_id)

        return query.all()

    def fetch_by_ligand_id(self, ligand_id, biomolecule_id, *expr, **kwargs):
        """
        Returns the SIFt of a ligand.
        """
        where = and_(BindingSiteResidue.ligand_id==ligand_id,
                     Contact.biomolecule_id==biomolecule_id,
                     Contact.is_same_entity==False,
                     *expr)

        query = Residue.query.join('Atoms','Contacts').filter(where)
        query = query.join(BindingSiteResidue,
                           and_(BindingSiteResidue.residue_id==Atom.residue_id,
                                BindingSiteResidue.entity_type_bm==Residue.entity_type_bm))
        query = query.group_by(Residue).order_by(Residue.residue_id)
        query = query.add_columns(*self._sift)

        return query.all()

    def fetch_by_ligand_id_and_atom_names(self, ligand_id, biomolecule_id,
                                          atom_names, *expr, **kwargs):
        """
        Returns the SIFt of a part of a ligand (defined by the input atom names).

        Queried Entities
        ----------------
        Contact, Atom, MatchAtom (Atom), Hetatm
        """
        MatchAtom = aliased(Atom)

        where = and_(MatchAtom.atom_name==func.any(atom_names),
                     Contact.biomolecule_id==biomolecule_id,
                     Contact.is_same_entity==False,
                     Hetatm.ligand_id==ligand_id, *expr)

        query = Contact.query.add_columns(Atom.residue_id.label('residue_id'))

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

        query = bgn.union_all(end).group_by('residue_id').order_by('residue_id')
        subquery = query.with_entities(Atom.residue_id, *self._sift).subquery()

        return self._fetch_sift(subquery)

    def fetch_by_ligand_fragment_id(self, ligand_fragment_id, biomolecule_id, *expr):
        """
        """
        where = and_(LigandFragmentAtom.ligand_fragment_id==ligand_fragment_id,
                     Contact.biomolecule_id==biomolecule_id,
                     Contact.is_same_entity==False,
                     *expr)

        query = Contact.query.add_columns(Atom.residue_id.label('residue_id'))

        bgn = query.join(Atom, and_(Atom.atom_id==Contact.atom_bgn_id,
                                    Atom.biomolecule_id==Contact.biomolecule_id))
        bgn = bgn.join(LigandFragmentAtom, LigandFragmentAtom.atom_id==Contact.atom_end_id)
        bgn = bgn.filter(where)

        end = query.join(Atom, and_(Atom.atom_id==Contact.atom_end_id,
                                    Atom.biomolecule_id==Contact.biomolecule_id))
        end = end.join(LigandFragmentAtom, LigandFragmentAtom.atom_id==Contact.atom_bgn_id)
        end = end.filter(where)

        query = bgn.union_all(end).group_by('residue_id').order_by('residue_id')
        subquery = query.with_entities(Atom.residue_id, *self._sift).subquery()

        return self._fetch_sift(subquery)

from ..models.contact import Contact
from ..models.atom import Atom
from ..models.hetatm import Hetatm
from ..models.residue import Residue
from ..models.ligandfragmentatom import LigandFragmentAtom
from ..models.bindingsite import BindingSiteResidue
