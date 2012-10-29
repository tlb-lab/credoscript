from sqlalchemy.sql.expression import and_, or_

from credoscript import interface_residues, phenotype_to_interface, variation_to_interface
from credoscript.mixins import PathAdaptorMixin
from credoscript.mixins.base import paginate

class InterfaceAdaptor(PathAdaptorMixin):
    """
    """
    def __init__(self, dynamic=False, paginate=False, per_page=100):
        self.query = Interface.query
        self.dynamic = dynamic
        self.paginate = paginate
        self.per_page = per_page

    def fetch_by_interface_id(self, interface_id):
        """
        Parameters
        ----------
        interface_id : int
            Primary key of the `Interface` in CREDO.

        Returns
        -------
        Interface
            CREDO `Interface` object having this interface_id as primary key.

        Examples
        --------
        >>> InterfaceAdaptor().fetch_by_interface_id(1)
        <Interface(1)>
        """
        return self.query.get(interface_id)

    @paginate
    def fetch_all_by_chain_id(self, chain_id, *expr, **kwargs):
        """
        """
        query = self.query.filter(and_(or_(Interface.chain_bgn_id==chain_id,
                                           Interface.chain_end_id==chain_id),
                                       *expr))

        return query

    @paginate
    def fetch_all_by_biomolecule_id(self, biomolecule_id, *expr, **kwargs):
        """
        Returns a list of `Interface`.

        Parameters
        ----------
        biomolecule_id : int
            `Biomolecule` identifier.

        Returns
        -------
        interfaces : list
            List of `Interface` objects.

         Examples
        --------
        >>> InterfaceAdaptor().fetch_all_by_biomolecule_id(1)
        >>> <Interface()>
        """
        query = self.query.filter(and_(Interface.biomolecule_id==biomolecule_id,
                                       *expr))

        return query

    @paginate
    def fetch_all_by_uniprot(self, uniprot, *expr, **kwargs):
        """
        """
        bgn = self.query.join('ChainBgn','XRefs')
        bgn = bgn.filter(and_(XRef.source=='UniProt', XRef.xref==uniprot, *expr))

        end = self.query.join('ChainEnd','XRefs')
        end = end.filter(and_(XRef.source=='UniProt', XRef.xref==uniprot, *expr))

        return bgn.union(end)

    @paginate
    def fetch_all_by_cath_dmn(self, cath, *expr, **kwargs):
        """
        """
        where = and_(Peptide.cath==cath, *expr)

        query = self.query.join(interface_residues,
                                interface_residues.c.interface_id==Interface.interface_id)

        bgn = query.join(Peptide,
                         Peptide.residue_id==interface_residues.c.residue_bgn_id)
        bgn = bgn.filter(where)

        end = query.join(Peptide,
                         Peptide.residue_id==interface_residues.c.residue_end_id)
        end = end.filter(where)

        return bgn.union(end)

    @paginate
    def fetch_all_by_phenotype_id(self, phenotype_id, *expr, **kwargs):
        """
        Returns all interfaces whose interacting residues can be linked to
        variations matching the given phenotype_id.
        """
        query = self.query.join(phenotype_to_interface,
                                phenotype_to_interface.c.interface_id==Interface.interface_id)
        query = query.filter(and_(phenotype_to_interface.c.phenotype_id==phenotype_id, *expr))

        return query

    @paginate
    def fetch_all_in_contact_with_variation_id(self, variation_id, *expr, **kwargs):
        """
        Returns all interfaces whose residues are in in contact with residues
        that can be linked to variations with the given variation_id.
        """
        query = self.query.join(variation_to_interface,
                                variation_to_interface.c.interface_id==Interface.interface_id)
        query = query.filter(and_(variation_to_interface.c.variation_id==variation_id,
                                  *expr))

        return query.distinct()

from ..models.interface import Interface
from ..models.peptide import Peptide
from ..models.xref import XRef