from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import and_, func

from credoscript import residue_interaction_pairs
from credoscript.mixins import PathAdaptorMixin, ResidueAdaptorMixin
from credoscript.mixins.base import paginate

class ResidueAdaptor(PathAdaptorMixin, ResidueAdaptorMixin):
    """
    """
    def __init__(self, dynamic=False, paginate=False, per_page=100):
        self.query = Residue.query
        self.dynamic = dynamic
        self.paginate = paginate
        self.per_page = per_page

    @paginate
    def fetch_all_by_ligand_id(self, ligand_id, *expr, **kwargs):
        """
        Returns a list of `Residues` that are part of the ligand with the given identifier.

        Parameters
        ----------
        ligand_id : int
            `Ligand` identifier.
        *expr : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried Entities
        ----------------
        Residue, LigandComponent

        Returns
        -------
        contacts : list
            List of `Residue` objects.

         Examples
        --------
        >>> ResidueAdaptor().fetch_all_by_ligand_id(4343)
        [<Atom(C01  )>, <Atom(C02  )>, <Atom(N03  )>, <Atom(C04  )>, <Atom(O05  )>,...]
        """
        query = self.query.join(LigandComponent,
                                LigandComponent.residue_id==Residue.residue_id)
        query = query.filter(and_(LigandComponent.ligand_id==ligand_id, *expr))

        return query

    @paginate
    def fetch_all_in_contact_with_residue_id(self, residue_id, *expr, **kwargs):
        """
        Returns all the Residues that are in contact with the Residue having the
        specified residue_id.

        Parameters
        ----------
        residue_id : int
            Primary key of the Residue.
        *expr : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Returns
        -------
        residues : list
            Residues that are in contact with the Residue having the specified
            residue_id.

        Queried Entities
        ----------------
        Residue, residue_interaction_pairs

        Examples
        --------
        >>>> ResidueAdaptor().fetch_all_in_contact_with_residue_id(271510)
        [<Residue(ILE 160 )>, <Residue(TYR 159 )>, <Residue(ALA 192 )>,
         <Residue(MSE 158 )>, <Residue(TYR 191 )>, <Residue(ALA 207 )>,
         <Residue(VAL 1532 )>, <Residue(GLN 206 )>, <Residue(ALA 190 )>,
         <Residue(MSE 210 )>, <Residue(LEU 203 )>]
        """
        bgn = self.query.join(residue_interaction_pairs,
                              residue_interaction_pairs.c.residue_bgn_id==Residue.residue_id)
        bgn = bgn.filter(and_(residue_interaction_pairs.c.residue_end_id==residue_id,
                              *expr))

        end = self.query.join(residue_interaction_pairs,
                              residue_interaction_pairs.c.residue_end_id==Residue.residue_id)
        end = end.filter(and_(residue_interaction_pairs.c.residue_bgn_id==residue_id,
                              *expr))

        return bgn.union(end)

    @paginate
    def fetch_all_in_contact_with_ligand_id(self, ligand_id, *expr, **kwargs):
        """
        Returns all residues that are in contact with the ligand having the specified
        ligand identifier.

        Parameters
        ----------
        ligand_id : int
            `Ligand` identifier.
        *expr : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried Entities
        ----------------
        Residue, BindingSiteResidue

        Returns
        -------
        residues : list
            List of `Residue` objects.
        """
        query = self.query.join(BindingSiteResidue,
                                BindingSiteResidue.residue_id==Residue.residue_id)
        query = query.filter(and_(BindingSiteResidue.ligand_id==ligand_id, *expr))

        return query

    @paginate
    def fetch_all_in_contact_with_ligand_fragment_id(self, ligand_fragment_id,
                                                     biomolecule_id, *expr,
                                                     **kwargs):
        """
        Returns all residues that are in contact with the ligand fragment having the specified
        identifier.

        Parameters
        ----------
        ligand_fragment_id : int
            `LigandFragment` identifier.
        biomolecule_id : int

        *expr : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried Entities
        ----------------
        Residue, Atom, Contact, ligand_fragment_atoms

        Returns
        -------
        residues : list
            List of `Residue` objects.
        """
        where = and_(LigandFragmentAtom.ligand_fragment_id==ligand_fragment_id,
                     Contact.biomolecule_id==Atom.biomolecule_id,
                     Contact.biomolecule_id==biomolecule_id,
                     *expr)

        query = self.query.join((Atom, Atom.residue_id==Residue.residue_id))

        bgn = query.join(Contact, Contact.atom_bgn_id==Atom.atom_id)
        bgn = bgn.join(LigandFragmentAtom, LigandFragmentAtom.atom_id==Contact.atom_end_id)
        bgn = bgn.filter(where)

        end = query.join(Contact, Contact.atom_end_id==Atom.atom_id)
        end = end.join(LigandFragmentAtom, LigandFragmentAtom.atom_id==Contact.atom_bgn_id)
        end = end.filter(where)

        query = bgn.union(end)

        return query

    @paginate
    def fetch_all_in_contact_with_ligand_id_and_atom_names(self, ligand_id, biomolecule_id,
                                                           atom_names, *expr, **kwargs):
        """
        Returns all residues that are in contact with the ligand atoms that are
        part of the ligand with the given ligand_id and its atoms that match the
        given atom names.
        """
        MatchAtom = aliased(Atom)

        where = and_(MatchAtom.atom_name==func.any(atom_names),
                     Contact.biomolecule_id==biomolecule_id,
                     Hetatm.ligand_id==ligand_id, *expr)

        query = self.query.select_from(Contact)

        bgn = query.join('AtomBgn','Residue')
        bgn = bgn.join(MatchAtom, and_(MatchAtom.atom_id==Contact.atom_end_id,
                                       MatchAtom.biomolecule_id==Contact.biomolecule_id))
        bgn = bgn.join(Hetatm, Hetatm.atom_id==MatchAtom.atom_id)
        bgn = bgn.filter(where).distinct()

        end = query.join('AtomEnd','Residue')
        end = end.join(MatchAtom, and_(MatchAtom.atom_id==Contact.atom_bgn_id,
                                       MatchAtom.biomolecule_id==Contact.biomolecule_id))
        end = end.join(Hetatm, Hetatm.atom_id==MatchAtom.atom_id)
        end = end.filter(where).distinct()

        return bgn.union(end)

from ..models.contact import Contact
from ..models.atom import Atom
from ..models.hetatm import Hetatm
from ..models.residue import Residue
from ..models.ligandcomponent import LigandComponent
from ..models.ligandfragmentatom import LigandFragmentAtom
from ..models.bindingsite import BindingSiteResidue
