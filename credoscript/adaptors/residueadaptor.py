from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import and_

from credoscript import binding_sites, interface_residues, residue_interaction_pairs
from credoscript.mixins import PathAdaptorMixin, ResidueAdaptorMixin
from credoscript.mixins.base import paginate

class ResidueAdaptor(PathAdaptorMixin, ResidueAdaptorMixin):
    """
    """
    def __init__(self, paginate=False, per_page=100):
        self.query = Residue.query
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
    def fetch_all_by_interface_id(self, interface_id, *expr, **kwargs):
        """
        Returns all the residues (including solvents) that are interacting across
        the interface.

        Parameters
        ----------
        interface_id : int
            Primary key of the interface.
        *expr : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried Entities
        ----------------
        Residue, interface_residues

        Returns
        -------
        contacts : list
            List of residues.

         Examples
        --------
        >>> interface = InterfaceAdaptor().fetch_by_interface_id(128)
        >>> interface.get_residues(Residue.entity_type_bm==32)
        >>> [<Residue(VAL 32 )>, <Residue(THR 91 )>, <Residue(LEU 23 )>,
             <Residue(ASP 30 )>, <Residue(GLY 49 )>, <Residue(ARG 87 )>,...]
        """
        whereclause = and_(interface_residues.c.interface_id==interface_id, *expr)

        bgn = self.query.join(interface_residues,
                              interface_residues.c.residue_bgn_id==Residue.residue_id)
        bgn = bgn.filter(whereclause)
        
        end = self.query.join(interface_residues,
                              interface_residues.c.residue_end_id==Residue.residue_id)
        end = end.filter(whereclause)

        query = bgn.union(end)

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
        Residue, binding_sites

        Returns
        -------
        residues : list
            List of `Residue` objects.
        """
        query = self.query.join(binding_sites, binding_sites.c.residue_id==Residue.residue_id)
        query = query.filter(and_(binding_sites.c.ligand_id==ligand_id, *expr))

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

from ..models.contact import Contact
from ..models.atom import Atom
from ..models.residue import Residue
from ..models.chain import Chain
from ..models.ligandcomponent import LigandComponent
from ..models.ligandfragmentatom import LigandFragmentAtom